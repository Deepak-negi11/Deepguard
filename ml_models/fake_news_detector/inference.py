"""
Fake News Detection using Pre-Trained HuggingFace BERT model.
Pattern adapted from industry-standard NLP classification pipelines.
Uses: mrm8488/bert-tiny-finetuned-fake-news-detection (HuggingFace Hub)
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Weights directory for local cache
WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights" / "fake_news"

# Singleton instance
_pipeline = None


def _get_pipeline():
    """Lazily load the HuggingFace text-classification pipeline."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    try:
        from transformers import pipeline as hf_pipeline

        # Try loading from local weights first
        if (WEIGHTS_DIR / "config.json").exists():
            logger.info(f"Loading Fake News model from local weights: {WEIGHTS_DIR}")
            _pipeline = hf_pipeline(
                "text-classification",
                model=str(WEIGHTS_DIR),
                tokenizer=str(WEIGHTS_DIR),
            )
        else:
            # Fallback: download directly from HuggingFace Hub
            logger.info("Local weights not found. Downloading from HuggingFace Hub...")
            _pipeline = hf_pipeline(
                "text-classification",
                model="mrm8488/bert-tiny-finetuned-fake-news-detection",
            )
        logger.info("Fake News model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Fake News model: {e}")
        _pipeline = None

    return _pipeline


def predict_news(text: str, url: str | None = None) -> dict:
    """
    Predict whether the given text is real or fake news.

    Returns:
        dict with keys: classification, confidence, anomalies
    """
    pipe = _get_pipeline()

    if pipe is None:
        return {
            "classification": "UNKNOWN",
            "confidence": 0.0,
            "anomalies": [
                {"type": "error", "description": "Model failed to load", "severity": "high"}
            ],
        }

    # Run inference (truncate to BERT's 512 token limit)
    result = pipe(text[:512], truncation=True)[0]

    # BERT-tiny fake news output: LABEL_0 = Real, LABEL_1 = Fake
    label = result["label"]
    confidence = result["score"]

    is_fake = label == "LABEL_1"
    classification = "FAKE" if is_fake else "REAL"

    return {
        "classification": classification,
        "confidence": confidence,
        "anomalies": [
            {
                "type": "text_analysis",
                "description": f"Model classified text as {classification} with {confidence:.2%} confidence",
                "severity": "high" if is_fake else "low",
            }
        ],
    }
