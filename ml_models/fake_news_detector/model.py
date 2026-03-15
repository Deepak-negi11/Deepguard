from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn
from torchvision.models import ResNet50_Weights, resnet50
from transformers import AutoModel


@dataclass(slots=True)
class FakeNewsModelConfig:
    text_model_name: str = "bert-base-uncased"
    dropout: float = 0.3
    embed_dim: int = 768
    num_heads: int = 8


class FakeNewsDetector(nn.Module):
    def __init__(self, config: FakeNewsModelConfig | None = None) -> None:
        super().__init__()
        self.config = config or FakeNewsModelConfig()
        self.text_encoder = AutoModel.from_pretrained(self.config.text_model_name)
        image_backbone = resnet50(weights=ResNet50_Weights.DEFAULT)
        self.image_backbone = nn.Sequential(*list(image_backbone.children())[:-1])
        self.text_projection = nn.Linear(768, self.config.embed_dim)
        self.image_projection = nn.Linear(2048, self.config.embed_dim)
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=self.config.embed_dim,
            num_heads=self.config.num_heads,
            dropout=0.1,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.Linear(self.config.embed_dim * 2 + 8, 256),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(64, 1),
        )

    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        source_features: Tensor,
        image_tensor: Tensor | None = None,
    ) -> Tensor:
        text_outputs = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask)
        text_cls = self.text_projection(text_outputs.last_hidden_state[:, 0, :])
        if image_tensor is None:
            image_cls = torch.zeros_like(text_cls)
        else:
            image_features = self.image_backbone(image_tensor).flatten(1)
            image_cls = self.image_projection(image_features)
        attended, _ = self.cross_attention(text_cls.unsqueeze(1), image_cls.unsqueeze(1), image_cls.unsqueeze(1))
        fused = torch.cat([text_cls, attended.squeeze(1), source_features], dim=1)
        return torch.sigmoid(self.classifier(fused))
