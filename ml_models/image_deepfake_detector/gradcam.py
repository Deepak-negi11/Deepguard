"""
Grad-CAM heatmap generator — implemented with pure numpy + opencv.
No external pytorch-grad-cam library needed.

How it works:
1. Load the ViT model directly (not via pipeline) with output_attentions=True
2. Run a forward pass to get attention weights from the last transformer block
3. Average the attention over heads → attention rollout map
4. Resize the attention map to the image size
5. Blend it as a colour heatmap over the original image
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

GRADCAM_OUTPUT_DIR = Path("/app/uploads/gradcam")


def _ensure_output_dir() -> None:
    GRADCAM_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_gradcam(image_path: str, hf_model_name: str = "Organika/sdxl-detector") -> str | None:
    """
    Generate an attention-based heatmap for *image_path*.

    Uses ViT attention rollout — a well-known alternative to Grad-CAM for
    Vision Transformers that requires only the model's own attention weights.

    Returns filename of the saved PNG (relative, not full path), or None on failure.
    File is saved to GRADCAM_OUTPUT_DIR and served at /api/v1/gradcam/<filename>.
    """
    try:
        import cv2
        import torch
        from PIL import Image
        from transformers import AutoFeatureExtractor, AutoModelForImageClassification
    except ImportError as exc:
        logger.warning("Grad-CAM deps missing (%s) — skipping heatmap", exc)
        return None

    try:
        _ensure_output_dir()

        # ── Load model with attentions enabled ────────────────────────────
        feature_extractor = AutoFeatureExtractor.from_pretrained(hf_model_name)
        model = AutoModelForImageClassification.from_pretrained(
            hf_model_name,
            output_attentions=True,
            attn_implementation="eager",  # needed for attention output on ViT
        )
        model.eval()

        # ── Preprocess image ──────────────────────────────────────────────
        pil_img = Image.open(image_path).convert("RGB")
        inputs = feature_extractor(images=pil_img, return_tensors="pt")

        # ── Forward pass ──────────────────────────────────────────────────
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        # ── Attention rollout ─────────────────────────────────────────────
        # outputs.attentions: list of (1, num_heads, seq_len, seq_len) per layer
        attentions = outputs.attentions  # list of tensors

        # Rollout: multiply attention maps through layers
        # Start with identity
        num_tokens = attentions[0].shape[-1]
        rollout = torch.eye(num_tokens)

        for attn in attentions:
            # Average over heads: (1, num_heads, seq_len, seq_len) → (seq_len, seq_len)
            attn_avg = attn[0].mean(dim=0)  # (seq_len, seq_len)
            # Add residual connection and normalize
            attn_avg = attn_avg + torch.eye(num_tokens)
            attn_avg = attn_avg / attn_avg.sum(dim=-1, keepdim=True)
            rollout = rollout @ attn_avg

        # CLS token (index 0) attention to all patches
        cls_attention = rollout[0, 1:]  # drop CLS itself → patch attentions

        # ── Reshape to spatial grid ───────────────────────────────────────
        grid_size = int(cls_attention.shape[0] ** 0.5)
        attention_map = cls_attention.reshape(grid_size, grid_size).numpy()

        # Normalize to [0, 1]
        attention_map = (attention_map - attention_map.min()) / (attention_map.max() - attention_map.min() + 1e-8)

        # ── Resize to image dimensions ────────────────────────────────────
        img_np = np.array(pil_img)
        h, w = img_np.shape[:2]
        attention_resized = cv2.resize(attention_map, (w, h), interpolation=cv2.INTER_CUBIC)

        # ── Apply colour map (COLORMAP_JET: blue=low, red=high) ──────────
        heatmap = cv2.applyColorMap(
            (attention_resized * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        # ── Blend with original image ─────────────────────────────────────
        blended = (img_np * 0.5 + heatmap_rgb * 0.5).clip(0, 255).astype(np.uint8)

        # ── Save ──────────────────────────────────────────────────────────
        out_filename = f"gradcam_{uuid.uuid4().hex[:12]}.png"
        out_path = GRADCAM_OUTPUT_DIR / out_filename
        Image.fromarray(blended).save(str(out_path))

        logger.info("Attention heatmap saved: %s", out_path)
        return out_filename

    except Exception as exc:
        logger.error("Grad-CAM generation failed: %s", exc, exc_info=True)
        return None
