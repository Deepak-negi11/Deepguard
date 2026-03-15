from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn
from torchvision.models import EfficientNet_B4_Weights, efficientnet_b4


@dataclass(slots=True)
class DeepfakeModelConfig:
    sequence_length: int = 30
    hidden_size: int = 256
    lstm_layers: int = 2
    dropout: float = 0.3
    ensemble_weights: tuple[float, float, float, float] = (0.35, 0.3, 0.2, 0.15)


class FrequencyAnalyzer(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(64, 1),
        )

    def forward(self, x: Tensor) -> Tensor:
        return self.network(x)


class DeepfakeEnsembleDetector(nn.Module):
    """Video deepfake detector with spatial, temporal, and frequency branches."""

    def __init__(self, config: DeepfakeModelConfig | None = None, pretrained: bool = True) -> None:
        super().__init__()
        self.config = config or DeepfakeModelConfig()
        weights = EfficientNet_B4_Weights.DEFAULT if pretrained else None
        backbone = efficientnet_b4(weights=weights)
        self.spatial_features = backbone.features
        self.spatial_pool = nn.AdaptiveAvgPool2d(1)
        self.spatial_classifier = nn.Sequential(
            nn.Dropout(self.config.dropout),
            nn.Linear(1792, 512),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(512, 1),
        )
        self.temporal_lstm = nn.LSTM(
            input_size=1792,
            hidden_size=self.config.hidden_size,
            num_layers=self.config.lstm_layers,
            dropout=self.config.dropout,
            batch_first=True,
            bidirectional=True,
        )
        self.temporal_head = nn.Sequential(
            nn.Linear(self.config.hidden_size * 2, 128),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(128, 1),
        )
        self.frequency_analyzer = FrequencyAnalyzer()
        self.landmark_head = nn.Sequential(
            nn.Linear(136, 64),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(64, 1),
        )

    def _extract_frame_embeddings(self, frames: Tensor) -> Tensor:
        batch_size, steps, channels, height, width = frames.shape
        flattened = frames.view(batch_size * steps, channels, height, width)
        features = self.spatial_features(flattened)
        pooled = self.spatial_pool(features).flatten(1)
        return pooled.view(batch_size, steps, -1)

    def forward(self, frames: Tensor, frequency_maps: Tensor, landmarks: Tensor | None = None) -> dict[str, Tensor]:
        embeddings = self._extract_frame_embeddings(frames)
        spatial_logits = self.spatial_classifier(embeddings.mean(dim=1))
        temporal_output, _ = self.temporal_lstm(embeddings)
        temporal_logits = self.temporal_head(temporal_output[:, -1, :])
        frequency_logits = self.frequency_analyzer(frequency_maps)
        if landmarks is None:
            landmarks = torch.zeros(frames.shape[0], 136, device=frames.device, dtype=frames.dtype)
        landmark_logits = self.landmark_head(landmarks)

        component_logits = {
            "spatial_cnn": spatial_logits,
            "temporal_lstm": temporal_logits,
            "frequency_analysis": frequency_logits,
            "facial_landmarks": landmark_logits,
        }
        probabilities = {name: torch.sigmoid(logits) for name, logits in component_logits.items()}
        stacked = torch.stack([probabilities[name].squeeze(-1) for name in component_logits], dim=1)
        weights = frames.new_tensor(self.config.ensemble_weights).unsqueeze(0)
        ensemble_score = (stacked * weights).sum(dim=1, keepdim=True)
        probabilities["ensemble_score"] = ensemble_score
        return probabilities
