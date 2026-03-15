from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer

from .model import FakeNewsDetector
from .utils import build_source_features, normalize_article_text


@dataclass(slots=True)
class TrainingConfig:
    dataset_path: str
    batch_size: int = 8
    epochs: int = 3
    learning_rate: float = 2e-5


class FakeNewsDataset(Dataset):
    def __init__(self, dataset_path: str) -> None:
        self.rows = pd.read_csv(dataset_path)
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows.iloc[index]
        tokens = self.tokenizer(
            normalize_article_text(row["text"]),
            truncation=True,
            padding="max_length",
            max_length=512,
            return_tensors="pt",
        )
        return {
            "input_ids": tokens["input_ids"].squeeze(0),
            "attention_mask": tokens["attention_mask"].squeeze(0),
            "source_features": build_source_features(row.get("url")).float(),
            "label": torch.tensor([float(row["label"])], dtype=torch.float32),
        }


def train(config: TrainingConfig) -> FakeNewsDetector:
    dataset = FakeNewsDataset(config.dataset_path)
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FakeNewsDetector().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    criterion = nn.BCELoss()

    model.train()
    for _ in range(config.epochs):
        for batch in loader:
            score = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                source_features=batch["source_features"].to(device),
            )
            loss = criterion(score, batch["label"].to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    return model
