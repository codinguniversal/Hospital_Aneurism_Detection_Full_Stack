import base64
import io
import numpy as np
import torch
import torch.nn.functional as F


def get_target_layer(model):
    """
    Automatically select a suitable final convolutional layer for Grad-CAM.

    Your project uses:
    - EfficientNetV2 for Cnn2dAdapter25
    - ResNet50 for Cnn2dAdapter12 and Cnn2dAdapter13
    """
    backbone = model.backbone

    # ResNet50 backbone
    if hasattr(backbone, "layer4"):
        return backbone.layer4[-1]

    # EfficientNet / EfficientNetV2 backbone
    if hasattr(backbone, "conv_head"):
        return backbone.conv_head

    # Fallback for other timm models
    if hasattr(backbone, "blocks"):
        return backbone.blocks[-1]

    raise ValueError("Could not automatically find a target layer for Grad-CAM.")


class GradCAM:
    """
    Grad-CAM implementation for your CNN models.

    Your processed input shape is:
        [D, B, C, H, W]

    Inside your model forward it becomes:
        [B, D, H, W]

    Here D works as the image channels:
        model25 -> 32 channels
        model12/model13 -> 256 channels
    """

    def __init__(self, model, target_layer, device):
        self.model = model
        self.target_layer = target_layer
        self.device = device

        self.activations = None
        self.gradients = None

        self.forward_handle = self.target_layer.register_forward_hook(
            self._save_activation
        )

    def _save_activation(self, module, input_tensor, output_tensor):
        self.activations = output_tensor

        def _save_gradient(grad):
            self.gradients = grad

        output_tensor.register_hook(_save_gradient)

    def close(self):
        self.forward_handle.remove()

    def __call__(self, x, requested_class_idx=None):
        """
        Generate Grad-CAM heatmap.

        Args:
            x:
                Preprocessed model input.
            requested_class_idx:
                Target class index from LABEL_COLS.

        Returns:
            cam:
                2D Grad-CAM heatmap normalized between 0 and 1.
            logits:
                Model logits after converting 13-class output into 14 labels if needed.
            class_idx:
                Class index used for explanation.
            slice_importance:
                Estimated channel/slice importance using input gradients.
        """
        self.model.eval()

        x = x.detach().clone().to(self.device)
        x.requires_grad_(True)

        self.model.zero_grad(set_to_none=True)

        with torch.enable_grad():
            raw_logits = self.model(x)

            # Some models output 13 classes only.
            # For them, "Aneurysm Present" is calculated as max of 13 location logits.
            if raw_logits.shape[1] == 13:
                aneurysm_present_logit = torch.max(
                    raw_logits[:, 0:13],
                    dim=1,
                    keepdim=True
                ).values

                logits = torch.cat(
                    [raw_logits[:, 0:13], aneurysm_present_logit],
                    dim=1
                )
            else:
                logits = raw_logits

            if requested_class_idx is None:
                class_idx = int(torch.argmax(logits[0]).item())
            else:
                if requested_class_idx >= logits.shape[1]:
                    raise ValueError(
                        f"Requested class index {requested_class_idx} "
                        f"is outside model output size {logits.shape[1]}."
                    )
                class_idx = int(requested_class_idx)

            score = logits[0, class_idx]
            score.backward()

        if self.activations is None:
            raise RuntimeError("Grad-CAM failed: activations were not captured.")

        if self.gradients is None:
            raise RuntimeError("Grad-CAM failed: gradients were not captured.")

        # Grad-CAM formula:
        # weights = global average pooling of gradients
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)

        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)
        cam = torch.relu(cam)

        cam = F.interpolate(
            cam,
            size=x.shape[-2:],
            mode="bilinear",
            align_corners=False
        )

        cam = cam[0, 0].detach().cpu().numpy()
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)

        # Estimate which input channels/slices affected the prediction most.
        if x.grad is None:
            slice_importance = np.zeros(x.shape[0], dtype=np.float32)
        else:
            slice_importance = x.grad.detach().abs().mean(dim=(1, 2, 3, 4))
            slice_importance = slice_importance.cpu().numpy()
            slice_importance = slice_importance / (slice_importance.max() + 1e-8)

        return cam, logits.detach().cpu().numpy(), class_idx, slice_importance


def resize_float_image(image, target_h, target_w):
    """
    Resize a float image using PyTorch interpolation.
    """
    tensor = torch.from_numpy(image).float().unsqueeze(0).unsqueeze(0)

    resized = F.interpolate(
        tensor,
        size=(target_h, target_w),
        mode="bilinear",
        align_corners=False
    )

    return resized[0, 0].numpy()


def map_depth_importance_to_original_slices(channel_scores, original_depth):
    """
    The model input depth is resampled to 32 or 256 channels.
    This function maps those channel-importance scores back approximately
    to the original DICOM slice indices.
    """
    mapped_scores = np.zeros(original_depth, dtype=np.float32)

    if original_depth <= 0:
        return mapped_scores

    if len(channel_scores) == 0:
        return mapped_scores

    if len(channel_scores) == 1:
        mapped_scores[0] = float(channel_scores[0])
        return mapped_scores

    for channel_idx, score in enumerate(channel_scores):
        original_idx = int(
            round(channel_idx * (original_depth - 1) / (len(channel_scores) - 1))
        )
        mapped_scores[original_idx] += float(score)

    mapped_scores = mapped_scores / (mapped_scores.max() + 1e-8)
    return mapped_scores


def simple_heatmap_colormap(heatmap):
    """
    Create a simple RGB heatmap from a grayscale heatmap.
    No OpenCV or matplotlib required.
    """
    heatmap = heatmap.astype(np.float32)
    heatmap = heatmap - heatmap.min()
    heatmap = heatmap / (heatmap.max() + 1e-8)

    red = np.clip(heatmap * 255, 0, 255)
    green = np.clip((1.0 - np.abs(heatmap - 0.5) * 2.0) * 255, 0, 255)
    blue = np.clip((1.0 - heatmap) * 80, 0, 80)

    colored = np.stack([red, green, blue], axis=-1).astype(np.uint8)
    return colored


def encode_png_base64(rgb_image):
    """
    Encode RGB numpy image to PNG base64.
    """
    from PIL import Image

    buffer = io.BytesIO()
    Image.fromarray(rgb_image.astype(np.uint8)).save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def create_overlay_base64(slice_img, heatmap, alpha=0.45):
    """
    Creates PNG base64 overlay:
        grayscale DICOM slice + colored Grad-CAM heatmap.
    """
    slice_img = slice_img.astype(np.float32)
    slice_img = slice_img - slice_img.min()
    slice_img = slice_img / (slice_img.max() + 1e-8)

    base = (slice_img * 255).astype(np.uint8)
    base_rgb = np.stack([base, base, base], axis=-1)

    heatmap = heatmap.astype(np.float32)
    heatmap = heatmap - heatmap.min()
    heatmap = heatmap / (heatmap.max() + 1e-8)

    if heatmap.shape != slice_img.shape:
        heatmap = resize_float_image(
            heatmap,
            target_h=slice_img.shape[0],
            target_w=slice_img.shape[1]
        )

    colored_heatmap = simple_heatmap_colormap(heatmap)

    overlay = ((1.0 - alpha) * base_rgb + alpha * colored_heatmap)
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    return encode_png_base64(overlay)


def explain_ensemble_gradcam(
    volume,
    modality,
    models,
    device,
    preprocess_transforms,
    process_volume_functions,
    label_cols,
    target_label="Aneurysm Present",
    top_k=3
):
    """
    Generate Grad-CAM explanation for the ensemble.

    Args:
        volume:
            Original loaded DICOM volume.
        modality:
            CT/MR modality flag.
        models:
            Loaded ensemble models.
        device:
            CUDA or CPU.
        preprocess_transforms:
            Preprocessing transforms for each model.
        process_volume_functions:
            Volume preparation functions for each model.
        label_cols:
            LABEL_COLS list.
        target_label:
            Class name to explain.
        top_k:
            Number of most important slices to return.

    Returns:
        Dictionary containing Grad-CAM explanation and top slice overlays.
    """
    if target_label not in label_cols:
        raise ValueError(
            f"Unknown target_label '{target_label}'. "
            f"Available labels are: {label_cols}"
        )

    target_idx = label_cols.index(target_label)

    original_depth = volume.shape[0]
    original_h = volume.shape[1]
    original_w = volume.shape[2]

    all_heatmaps = []
    final_slice_scores = np.zeros(original_depth, dtype=np.float32)
    model_explanations = []

    for model_idx, model in enumerate(models):
        x = process_volume_functions[model_idx](
            volume,
            modality,
            preprocess_transforms[model_idx]
        )

        target_layer = get_target_layer(model)
        gradcam = GradCAM(model, target_layer, device)

        try:
            cam, logits, used_class_idx, slice_importance = gradcam(
                x,
                requested_class_idx=target_idx
            )
        finally:
            gradcam.close()

        cam_original_size = resize_float_image(
            cam,
            target_h=original_h,
            target_w=original_w
        )

        all_heatmaps.append(cam_original_size)

        mapped_slice_scores = map_depth_importance_to_original_slices(
            slice_importance,
            original_depth
        )

        final_slice_scores += mapped_slice_scores

        used_label = (
            label_cols[used_class_idx]
            if used_class_idx < len(label_cols)
            else str(used_class_idx)
        )

        model_explanations.append({
            "model_index": int(model_idx),
            "used_class_index": int(used_class_idx),
            "used_class_label": used_label
        })

    final_heatmap = np.mean(np.stack(all_heatmaps, axis=0), axis=0)
    final_heatmap = final_heatmap - final_heatmap.min()
    final_heatmap = final_heatmap / (final_heatmap.max() + 1e-8)

    final_slice_scores = final_slice_scores / (final_slice_scores.max() + 1e-8)

    top_slice_indices = np.argsort(final_slice_scores)[-top_k:][::-1]

    top_slices = []

    for slice_idx in top_slice_indices:
        overlay_base64 = create_overlay_base64(
            volume[slice_idx],
            final_heatmap
        )

        top_slices.append({
            "slice_index": int(slice_idx),
            "importance": float(final_slice_scores[slice_idx]),
            "overlay_png_base64": overlay_base64
        })

    return {
        "method": "Grad-CAM",
        "target_label": target_label,
        "note": (
            "Grad-CAM heatmap shows the spatial area used by the CNN. "
            "Top slice indices are estimated from input-gradient channel importance."
        ),
        "model_explanations": model_explanations,
        "top_slices": top_slices
    }