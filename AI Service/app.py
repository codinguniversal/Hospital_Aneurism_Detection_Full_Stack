
import os
import tempfile

# Force Python and underlying C++ matrix engines to use your spacious D: drive folder
os.environ["TMPDIR"] = r"D:\AI_Temp"
os.environ["TEMP"] = r"D:\AI_Temp"
os.environ["TMP"] = r"D:\AI_Temp"
os.environ["HF_HOME"] = r"D:\AI_Temp\hf_cache"

# Explicitly ensure that this folder exists right now on your D: drive
os.makedirs(r"D:\AI_Temp", exist_ok=True)

# Instruct Python's global temp library to reset its core baseline path pointer
tempfile.tempdir = r"D:\AI_Temp"
# ==============================================================================

import shutil
import zipfile
import numpy as np
import torch
import torch.nn.functional as F
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import albumentations as A

# استيراد الدوال من ملفاتك ( src )
from src.load_dicoms import load_dicom_serie, DicomSerieError
from src.nn_models import Cnn2dAdapter25, Cnn2dAdapter12, Cnn2dAdapter13, apply_transform_1d
from src.constants import LABEL_COLS
from src.gradcam_utils import explain_ensemble_gradcam


# 1. إنشاء الـ App وتفعيل الـ CORS للربط مع الويبسايت
app = FastAPI(title="RSNA Intracranial Aneurysm Detection API - ZIP Enabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تحديد الجهاز المستهدف (GPU إذا وجد، وإلا CPU)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODELS = []


# ==========================================
# 2. إعدادات معالجة الصور (Transforms & Pipelines)
# ==========================================
preprocess25 = A.Compose([A.Resize(384, 384)])

transform_train25 = A.Compose([
    A.Resize(384, 384),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.ShiftScaleRotate(
        shift_limit=0.0625,
        scale_limit=0.1,
        rotate_limit=30,
        p=.5
    ),
    A.ElasticTransform(p=0.4),
    A.GridDistortion(p=0.4),
])

preprocess12 = A.Compose([
    A.Resize(512, 512),
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

transform_train12 = A.Compose([
    A.Resize(height=512, width=512),
    A.ShiftScaleRotate(
        shift_limit=0.1,
        scale_limit=0.1,
        rotate_limit=10,
        p=0.5
    ),
    A.Affine(shear=10, p=0.5),
    A.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])

preprocess13 = A.Compose([
    A.Resize(512, 512),
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

transform_train13 = A.Compose([
    A.Resize(height=512, width=512),
    A.ShiftScaleRotate(
        shift_limit=0.1,
        scale_limit=0.1,
        rotate_limit=10,
        p=0.5
    ),
    A.Affine(shear=10, p=0.5),
    A.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])


# ==========================================
# 3. دوال تجهيز الـ Volumes للموديلات
# ==========================================
def apply_volume_transform(volume, transform):
    transformed = transform(image=volume)["image"]

    if transformed.ndim != 3:
        raise ValueError(
            "Volume transform must preserve a 3D array shaped "
            f"(height, width, slices), got shape {transformed.shape}."
        )

    return transformed


def process_volume25(volume, modality, transform):
    img_3d_seq = apply_transform_1d(volume, modality)
    volume = np.stack(img_3d_seq, axis=0)

    # تظبيط الأبعاد لـ (H, W, Channels)
    volume = volume.transpose(1, 2, 0)
    volume = apply_volume_transform(volume, transform)
    volume = volume.transpose(2, 0, 1)

    volume = torch.from_numpy(volume).unsqueeze(1)

    d, c, h, w = volume.shape

    volume = volume.unsqueeze(1).permute(1, 2, 0, 3, 4)

    volume = F.interpolate(
        volume,
        size=(32, h, w),
        mode="trilinear",
        align_corners=False
    )

    return volume.permute(2, 0, 1, 3, 4)


def process_volume12_13(volume, modality, transform):
    img_3d_seq = apply_transform_1d(volume, modality)
    volume = np.stack(img_3d_seq, axis=0)
    volume = 255 * volume.astype(np.uint8)

    # تظبيط الأبعاد لـ (H, W, Channels)
    volume = volume.transpose(1, 2, 0)
    volume = apply_volume_transform(volume, transform)
    volume = volume.transpose(2, 0, 1)

    volume = torch.from_numpy(volume).unsqueeze(1)

    d, c, h, w = volume.shape

    volume = volume.unsqueeze(1).permute(1, 2, 0, 3, 4)

    volume = F.interpolate(
        volume,
        size=(256, h, w),
        mode="trilinear",
        align_corners=False
    )

    return volume.permute(2, 0, 1, 3, 4)


# ==========================================
# 4. تحميل الموديلات
# ==========================================
@app.on_event("startup")
def startup_load_models():
    global MODELS

    print(f"Server starting on {DEVICE}. Loading Ensemble Models...")

    MODEL_PATHS = [
        "model_weights/model25.pt",
        "model_weights/model12.pt",
        "model_weights/model13.pt"
    ]

    try:
        model25 = Cnn2dAdapter25(32).to(DEVICE).eval()
        model25.load_state_dict(
            torch.load(
                MODEL_PATHS[0],
                map_location=DEVICE,
                weights_only=True
            )
        )

        model12 = Cnn2dAdapter12(256).to(DEVICE).eval()
        model12.load_state_dict(
            torch.load(
                MODEL_PATHS[1],
                map_location=DEVICE,
                weights_only=True
            )
        )

        model13 = Cnn2dAdapter13(256).to(DEVICE).eval()
        model13.load_state_dict(
            torch.load(
                MODEL_PATHS[2],
                map_location=DEVICE,
                weights_only=True
            )
        )

        MODELS = [model25, model12, model13]

        print("Models loaded successfully! Server is ready.")

    except Exception as e:
        print(f"CRITICAL ERROR: Could not load models. Error: {e}")


# ==========================================
# 5. الـ API Endpoint الأساسية لاستقبال ZIP
# ==========================================
@app.post("/predict")
async def predict_aneurysm_zip(
    file: UploadFile = File(...),
    explain: bool = True,
    target_label: str = "Aneurysm Present"
):
    """
    Normal prediction:
        POST /predict

    Prediction with Grad-CAM:
        POST /predict?explain=true

    Prediction with Grad-CAM for specific label:
        POST /predict?explain=true&target_label=Basilar%20Tip
    """

    print(f"Grad-CAM enabled, target label: {target_label}")

    if not MODELS:
        raise HTTPException(
            status_code=500,
            detail="Models are not loaded on the server."
        )

    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed."
        )

    # 🚀 Explicitly force mkdtemp to build within our high capacity drive path
    base_dir = tempfile.mkdtemp(dir=r"D:\AI_Temp")
    zip_path = os.path.join(base_dir, file.filename)
    extract_dir = os.path.join(base_dir, "extracted")

    try:
        # 1. حفظ ملف الـ ZIP المرفوع
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. فك ضغط الملف
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # 3. تجميع مسارات ملفات DICOM
        all_dicom_filepaths = []

        for root, _, files in os.walk(extract_dir):
            for file_name in files:
                if file_name.lower().endswith(".dcm"):
                    all_dicom_filepaths.append(
                        os.path.join(root, file_name)
                    )

        all_dicom_filepaths.sort()

        if len(all_dicom_filepaths) == 0:
            raise HTTPException(
                status_code=400,
                detail="No DICOM (.dcm) files found inside the ZIP."
            )

        # 4. استخراج البيانات
        print(f"Processing {len(all_dicom_filepaths)} DICOM slices for patient...")

        result = load_dicom_serie(
            "test_patient",
            all_dicom_filepaths,
            load_data=True
        )

        recoverable_dicom_warnings = {
            DicomSerieError.SLICE_SPACING_INCONSISTENCY,
            DicomSerieError.METADATA_INCONSISTENT,
        }

        if (
            result[1] != DicomSerieError.NO_ERROR
            and result[1] not in recoverable_dicom_warnings
        ):
            raise HTTPException(
                status_code=400,
                detail=f"DICOM Error: {result[1].name}"
            )

        dicom_warning = (
            result[1].name
            if result[1] in recoverable_dicom_warnings
            else None
        )

        volume = result[2]
        modality = result[6]

        # 5. تشغيل الـ AI Pipeline
        preprocess_transforms = [
            preprocess25,
            preprocess12,
            preprocess13
        ]

        train_transforms = [
            transform_train25,
            transform_train12,
            transform_train13
        ]

        process_volumes = [
            process_volume25,
            process_volume12_13,
            process_volume12_13
        ]

        weights = [1.0, 1.0, 1.0]
        TTA_NUM = 2

        final_logits_per_model = []

        with torch.no_grad():
            for i in range(len(MODELS)):
                model_logits = []
                weight = weights[i]

                # Main prediction
                volume_pre = process_volumes[i](
                    volume,
                    modality,
                    preprocess_transforms[i]
                )

                logits = MODELS[i](volume_pre.to(DEVICE))

                if logits.shape[1] == 13:
                    aneurysm_present = torch.max(
                        logits[:, 0:13],
                        dim=1,
                        keepdim=True
                    ).values

                    logits = torch.cat(
                        [logits[:, 0:13], aneurysm_present],
                        dim=1
                    )

                model_logits.append(logits)

                # Test Time Augmentation
                for _ in range(TTA_NUM):
                    volume_tta = process_volumes[i](
                        volume,
                        modality,
                        train_transforms[i]
                    )

                    logits_tta = MODELS[i](volume_tta.to(DEVICE))

                    if logits_tta.shape[1] == 13:
                        aneurysm_present = torch.max(
                            logits_tta[:, 0:13],
                            dim=1,
                            keepdim=True
                        ).values

                        logits_tta = torch.cat(
                            [logits_tta[:, 0:13], aneurysm_present],
                            dim=1
                        )

                    model_logits.append(logits_tta)

                model_stacked_logits = torch.cat(model_logits)
                model_averaged_logits = torch.mean(model_stacked_logits, 0)

                final_logits_per_model.append(
                    weight * model_averaged_logits
                )

            averaged_logits = torch.stack(final_logits_per_model).sum(dim=0)

            probabilities = torch.sigmoid(
                averaged_logits
            ).cpu().detach().numpy().flatten()

        # 6. تحضير النتيجة
        response_data = {
            label: float(prob)
            for label, prob in zip(LABEL_COLS, probabilities)
        }

        overall_prediction = {
            "Aneurysm Present": response_data.pop("Aneurysm Present")
        }

        content = {
            "status": "success",
            "overall_prediction": overall_prediction,
            "detailed_locations": response_data,
            "message": f"Analyzed {len(all_dicom_filepaths)} slices successfully.",
            "dicom_warning": dicom_warning,
            "explain_requested": True,
            "target_label": target_label
        }

        # 7. Explainable AI باستخدام Grad-CAM
        # مهم جدًا: Grad-CAM يجب أن يعمل خارج torch.no_grad()
        print("Starting Grad-CAM explanation...")

        explanation = explain_ensemble_gradcam(
            volume=volume,
            modality=modality,
            models=MODELS,
            device=DEVICE,
            preprocess_transforms=preprocess_transforms,
            process_volume_functions=process_volumes,
            label_cols=LABEL_COLS,
            target_label=target_label,
            top_k=3
        )

        content["explainability"] = explanation

        print("Grad-CAM explanation added to response.")

        return JSONResponse(content=content)

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # 8. مسح الملفات المؤقتة
        shutil.rmtree(base_dir, ignore_errors=True)
