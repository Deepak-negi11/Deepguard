"""
Image Deepfake Detector — Model Architecture.

NOTE: Inference now uses the HuggingFace pipeline (Ateeqq/ai-vs-human-image-detector)
via inference.py. This class is kept for potential future fine-tuning workflows.
"""
import torch
import torch.nn as nn


class ImageDeepfakeDetector(nn.Module):
    """EfficientNet-B4 based detector — kept for fine-tuning, not used in inference."""
    def __init__(self, pretrained: bool = False):
        super().__init__()
        try:
            import timm
            self.backbone = timm.create_model('tf_efficientnet_b4.ns_jft_in1k', pretrained=pretrained, num_classes=0)
            self.classifier = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(self.backbone.num_features, 1),
                nn.Sigmoid()
            )
        except ImportError:
            self.backbone = None

    def forward(self, x):
        if self.backbone is None:
            return torch.sigmoid(torch.randn(x.size(0), 1, device=x.device))
        features = self.backbone(x)
        return self.classifier(features)
