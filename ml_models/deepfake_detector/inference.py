"""
Video/Image Deepfake Detection using EfficientNetV2 + timm.
Pattern directly adapted from: Akshayredekar07/Multimodal-Deepfake-Detection
Reference: https://github.com/Akshayredekar07/Multimodal-Deepfake-Detection/blob/main/backend/app/image_detection.py
Also references: ondyari/FaceForensics detect_from_video.py (XceptionNet pattern)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

logger = logging.getLogger(__name__)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights" / "video_deepfake"


# ---------- EfficientNetV2 Model (from Akshayredekar07 repo) ----------
class EfficientNetV2Detector(nn.Module):
    """
    EfficientNetV2 deepfake detector using timm.
    Exactly as implemented in Akshayredekar07/Multimodal-Deepfake-Detection.
    """

    def __init__(self, num_classes: int = 1, dropout_rate: float = 0.3):
        super().__init__()
        try:
            from timm import create_model
            self.base_model = create_model("tf_efficientnetv2_s", pretrained=True, num_classes=0)
        except ImportError:
            # Fallback to torchvision EfficientNet
            from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
            backbone = efficientnet_v2_s(weights=EfficientNet_V2_S_Weights.DEFAULT)
            self.base_model = nn.Sequential(*list(backbone.children())[:-1])

        num_features = 1280  # EfficientNetV2-S feature dim
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(num_features, 512),
            nn.SiLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(dropout_rate),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if hasattr(self.base_model, "forward_features"):
            features = self.base_model.forward_features(x)
        else:
            features = self.base_model(x)
        out = self.classifier(features)
        if out.dim() == 2 and out.size(1) == 1:
            out = out.squeeze(1)
        return out


# ---------- Image Transform (from Akshayredekar07 repo) ----------
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
])

# Singleton
_model = None
_device = None


def _load_model():
    global _model, _device
    if _model is not None:
        return _model, _device

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Initializing EfficientNetV2 Video Detector on {_device}")

    _model = EfficientNetV2Detector()

    weights_path = WEIGHTS_DIR / "efficientnetb4_ffpp.pth"
    if weights_path.exists():
        try:
            state_dict = torch.load(weights_path, map_location=_device)
            _model.load_state_dict(state_dict, strict=False)
            logger.info(f"Loaded weights from {weights_path}")
        except Exception as e:
            logger.warning(f"Could not load custom weights: {e}. Using ImageNet pretrained.")

    _model.to(_device)
    _model.eval()
    return _model, _device


def _extract_frames(video_path: str | Path, num_frames: int = 10) -> list:
    """
    Extract frames from video using OpenCV.
    Pattern from ondyari/FaceForensics detect_from_video.py.
    """
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []

    # Sample frames evenly
    frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
    frames = []

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Convert BGR to RGB (OpenCV to PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            frames.append(pil_img)

    cap.release()
    return frames


def predict_video(video_path: str | Path) -> dict[str, Any]:
    """
    Detect deepfake in a video by analyzing sampled frames.
    Pattern from Akshayredekar07 (image detection) + ondyari (frame extraction).
    """
    model, device = _load_model()

    try:
        frames = _extract_frames(video_path, num_frames=10)
        if not frames:
            raise ValueError("No frames could be extracted from the video.")

        # Run inference on each frame
        frame_tensors = torch.stack([_transform(frame) for frame in frames]).to(device)

        with torch.no_grad():
            outputs = model(frame_tensors)
            probs = torch.sigmoid(outputs)

        # Average across frames
        avg_fake_prob = float(probs.mean().cpu())

        is_fake = avg_fake_prob >= 0.5
        classification = "FAKE" if is_fake else "REAL"
        confidence = avg_fake_prob if is_fake else (1.0 - avg_fake_prob)

        return {
            "classification": classification,
            "confidence": confidence,
            "anomalies": [
                {
                    "type": "frame_analysis",
                    "description": f"EfficientNetV2 detected {'manipulation' if is_fake else 'authentic content'} "
                                   f"across {len(frames)} frames with {confidence:.2%} confidence",
                    "severity": "high" if is_fake else "low",
                }
            ],
        }

    except Exception as e:
        logger.error(f"Video inference failed: {e}")
        return {
            "classification": "UNKNOWN",
            "confidence": 0.0,
            "anomalies": [{"type": "error", "description": str(e), "severity": "high"}],
        }
