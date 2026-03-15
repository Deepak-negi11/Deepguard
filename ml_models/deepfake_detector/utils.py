from __future__ import annotations

from pathlib import Path

import torch


def save_model_checkpoint(model: torch.nn.Module, target_path: str | Path) -> None:
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), target_path)


def binary_accuracy(predictions: torch.Tensor, labels: torch.Tensor) -> float:
    predicted = (predictions >= 0.5).float()
    return float((predicted == labels).float().mean().item())
