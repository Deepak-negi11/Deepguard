from __future__ import annotations

from dataclasses import dataclass

from torch import Tensor, nn


@dataclass(slots=True)
class AudioModelConfig:
    input_shape: tuple[int, int, int] = (1, 128, 128)
    dropout: float = 0.5


class AudioDeepfakeDetector(nn.Module):
    def __init__(self, config: AudioModelConfig | None = None) -> None:
        super().__init__()
        self.config = config or AudioModelConfig()
        self.network = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(128, 1),
        )

    def forward(self, spectrogram: Tensor) -> Tensor:
        return nn.functional.sigmoid(self.network(spectrogram))
