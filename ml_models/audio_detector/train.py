from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from .model import AudioDeepfakeDetector
from .utils import load_audio_spectrogram


@dataclass(slots=True)
class TrainingConfig:
    manifest_path: str
    batch_size: int = 16
    epochs: int = 10
    learning_rate: float = 1e-3


class AudioManifestDataset(Dataset):
    def __init__(self, manifest_path: str) -> None:
        self.rows = pd.read_csv(manifest_path)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.rows.iloc[index]
        spectrogram = load_audio_spectrogram(row["audio_path"])
        label = torch.tensor([float(row["label"])], dtype=torch.float32)
        return spectrogram, label


def train(config: TrainingConfig) -> AudioDeepfakeDetector:
    dataset = AudioManifestDataset(config.manifest_path)
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AudioDeepfakeDetector().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    criterion = nn.BCELoss()

    model.train()
    for _ in range(config.epochs):
        for spectrograms, labels in loader:
            outputs = model(spectrograms.to(device))
            loss = criterion(outputs, labels.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    return model
