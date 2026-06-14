import typing as tp
import numpy as np
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score


class ParticipantVisibleError(Exception):
    pass


def weighted_multilabel_auc(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    class_weights: tp.Optional[tp.List[float]] = [1.0] * 13 + [13.0],
) -> float:
    """
    Compute weighted AUC for multilabel classification.
    from official https://www.kaggle.com/code/metric/mean-weighted-columnwise-aucroc
    """
    y_true = np.asarray(y_true)
    y_scores = np.asarray(y_scores)
    n_classes = y_true.shape[1]

    # Get AUC for each class
    try:
        individual_aucs = roc_auc_score(y_true, y_scores, average=None)
    except Exception as e:
        print("Error type:", type(e).__name__)
        print("Error message:", e)
        raise ParticipantVisibleError(
            "AUC could not be calculated from given predictions."
        ) from None

    # Handle weights
    if class_weights is None:  # Uniform weights
        weights_array = np.ones(n_classes)
    else:
        weights_array = np.asarray(class_weights)

    # Check weight dimensions
    if len(weights_array) != n_classes:
        raise ValueError(
            f"Number of weights ({len(weights_array)}) must match "
            f"number of classes ({n_classes})"
        )

    # Check for non-negative weights
    if np.any(weights_array < 0):
        raise ValueError("All class weights must be non-negative")

    # Check that at least one weight is positive
    if np.sum(weights_array) == 0:
        raise ValueError("At least one class weight must be positive")

    # Normalize weights to sum to 1
    weights_array = weights_array / np.sum(weights_array)

    # Compute weighted average
    return np.sum(individual_aucs * weights_array)


def compute_metrics(
    full_y: torch.Tensor,
    full_logits: torch.Tensor,
    full_pred: torch.Tensor,
    sk_learn_metrics_pred_logits: tp.List[tp.Callable],
    sk_learn_metrics_pred: tp.List[tp.Callable],
) -> tp.Dict:
    full_y = full_y.detach().cpu().numpy()
    full_logits = torch.sigmoid(full_logits).detach().cpu().numpy()
    full_pred = full_pred.detach().cpu().numpy()

    results = {}
    for metric in sk_learn_metrics_pred_logits:
        results[metric.__name__] = metric(full_y, full_logits)
    for metric in sk_learn_metrics_pred:
        results[metric.__name__] = metric(full_y, full_pred)
    return results


def eval_model(
    model: nn.Module,
    dataloader: DataLoader,
    sk_learn_metrics_pred_2d: tp.List[tp.Callable],
    sk_learn_metrics_pred: tp.List[tp.Callable],
    device: torch.cuda.device,
    threshold: float = 0.5,
) -> tp.Dict:

    model.eval()
    full_y = torch.Tensor([]).to(device)
    full_logits = torch.Tensor([]).to(device)
    full_pred = torch.Tensor([]).to(device)

    with torch.no_grad():
        for X, y, lengths in dataloader:
            X = X.to(device)
            y = y.to(device)
            logits = model(X, lengths)
            aneurysm_present = torch.max(logits[:, 0:13], dim=1, keepdim=True).values
            logits_modified = torch.cat([logits[:, 0:13], aneurysm_present], dim=1)
            preds = (torch.sigmoid(logits_modified) > threshold).float()

            full_y = torch.cat([full_y, y])
            full_logits = torch.cat([full_logits, logits_modified])
            full_pred = torch.cat([full_pred, preds])
    return compute_metrics(
        full_y, full_logits, full_pred, sk_learn_metrics_pred_2d, sk_learn_metrics_pred
    )


def run_one_epoch(
    model: nn.Module,
    training_dataloader: DataLoader,
    optimizer: Optimizer,
    loss_function: nn.Module,
    scheduler: LRScheduler,
    device: torch.cuda.device,
    writer: SummaryWriter,
    epoch: int,
    sk_learn_metrics_pred_2d: tp.List[tp.Callable],
    sk_learn_metrics_pred: tp.List[tp.Callable],
    threshold: float = 0.5,
    accumulate_gradient: int = 8,
):

    running_loss = 0.0
    num_batch = len(training_dataloader)
    full_y_list = []
    full_logits_list = []
    full_pred_list = []

    model.train()
    optimizer.zero_grad()

    for batch, (X, y, lengths) in enumerate(training_dataloader):
        X = X.to(device)
        y = y.to(device)
        logits = model(X, lengths)

        true_loss = loss_function(logits[:, 0:13], y.float()[:, 0:13])
        loss = true_loss / accumulate_gradient
        # At the optimizer.step() it will make sum(loss) = sum(true_loss)/accumulate_gradient

        loss.backward()  # Compute a small graph to use less memory

        if (batch + 1) % accumulate_gradient == 0:
            optimizer.step()  # Sum the loss and compute gradints from it
            optimizer.zero_grad()  # Clear grads

        with torch.no_grad():
            aneurysm_present = torch.max(logits[:, 0:13], dim=1, keepdim=True).values
            logits_modified = torch.cat([logits[:, 0:13], aneurysm_present], dim=1)
            preds = (torch.sigmoid(logits_modified) > threshold).float()
            full_y_list.append(y.detach().cpu())
            full_logits_list.append(logits_modified.detach().cpu())
            full_pred_list.append(preds.detach().cpu())

        running_loss += true_loss.item()
        avg_loss = running_loss / (batch + 1.0)
        if batch % 1 == 0:
            writer.add_scalar("lengths", lengths[0], batch + epoch * num_batch)
            writer.add_scalar(
                "cuda memory_allocated",
                torch.cuda.memory_allocated() / 1024**2,
                batch + epoch * num_batch,
            )
            writer.add_scalar(
                "cuda memory_reserved",
                torch.cuda.memory_reserved() / 1024**2,
                batch + epoch * num_batch,
            )
            writer.add_scalar(
                "cuda max_memory_allocated",
                torch.cuda.max_memory_allocated() / 1024**2,
                batch + epoch * num_batch,
            )
            writer.add_scalar(
                "cuda max_memory_reserved",
                torch.cuda.max_memory_reserved() / 1024**2,
                batch + epoch * num_batch,
            )
            writer.add_scalar("Training Loss(avg)", avg_loss, batch + epoch * num_batch)
            writer.add_scalar(
                "Training Loss (raw)", true_loss.item(), batch + epoch * num_batch
            )
            writer.add_scalar(
                "Learning rate ", scheduler.get_last_lr()[0], batch + epoch * num_batch
            )

    if (batch + 1) % accumulate_gradient != 0:
        nn.utils.clip_grad_norm_(model.parameters(), 3.0)
        optimizer.step()
        optimizer.zero_grad()

    writer.flush()

    full_y = torch.cat(full_y_list)
    full_logits = torch.cat(full_logits_list)
    full_pred = torch.cat(full_pred_list)
    train_res = compute_metrics(
        full_y, full_logits, full_pred, sk_learn_metrics_pred_2d, sk_learn_metrics_pred
    )
    return train_res
