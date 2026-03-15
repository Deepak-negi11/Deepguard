from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from .model import DeepfakeEnsembleDetector
from .preprocessing import extract_frames, frames_to_frequency_maps, frames_to_tensor


@dataclass(slots=True)
class TrainingConfig:
    manifest_path: str
    batch_size: int = 4
    epochs: int = 10
    learning_rate: float = 1e-4


class DeepfakeManifestDataset(Dataset):
    def __init__(self, manifest_path: str) -> None:
        self.rows = pd.read_csv(manifest_path)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        row = self.rows.iloc[index]
        frames = extract_frames(row["video_path"])
        frame_tensor = frames_to_tensor(frames)
        frequency_tensor = frames_to_frequency_maps(frames).mean(dim=0)
        label = torch.tensor([float(row["label"])], dtype=torch.float32)
        return frame_tensor, frequency_tensor, label


def train(config: TrainingConfig) -> DeepfakeEnsembleDetector:
    dataset = DeepfakeManifestDataset(config.manifest_path)
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DeepfakeEnsembleDetector().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    criterion = nn.BCELoss()

    model.train()
    for _ in range(config.epochs):
        for frames, frequencies, labels in loader:
            outputs = model(frames.to(device), frequencies.to(device))
            predictions = outputs["ensemble_score"]
            loss = criterion(predictions, labels.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    return model
