"""
Fake news detection using a RoBERTa text-classification model.
Uses: hamzab/roberta-fake-news-classification (HuggingFace Hub)
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_ID = "hamzab/roberta-fake-news-classification"
WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights" / "fake_news" / "hamzab-roberta-fake-news-classification"

# Singleton instance
_pipeline = None


def get_news_model_source() -> str:
    return "local_weights" if (WEIGHTS_DIR / "config.json").exists() else "huggingface"


def _get_pipeline():
    """Lazily load the HuggingFace text-classification pipeline."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    try:
        from transformers import pipeline as hf_pipeline

        # Try loading from local weights first
        if (WEIGHTS_DIR / "config.json").exists():
            logger.info("Loading fake news model from local weights: %s", WEIGHTS_DIR)
            _pipeline = hf_pipeline(
                "text-classification",
                model=str(WEIGHTS_DIR),
                tokenizer=str(WEIGHTS_DIR),
            )
        else:
            logger.info("Local fake news weights not found. Loading %s from HuggingFace Hub...", MODEL_ID)
            _pipeline = hf_pipeline(
                "text-classification",
                model=MODEL_ID,
            )
        logger.info("Fake news model loaded successfully.")
    except Exception as e:
        logger.error("Failed to load fake news model: %s", e)
        _pipeline = None

    return _pipeline


def warm_news_model() -> bool:
    return _get_pipeline() is not None


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

    # Keep inputs bounded for transformer inference.
    result = pipe(text[:512], truncation=True)[0]

    label = str(result["label"]).strip().upper()
    confidence = result["score"]
    if label in {"FAKE", "FALSE"}:
        classification = "FAKE"
        severity = "high"
    elif label in {"REAL", "TRUE"}:
        classification = "REAL"
        severity = "low"
    else:
        classification = "UNKNOWN"
        severity = "medium"

    return {
        "classification": classification,
        "confidence": confidence,
        "anomalies": [
            {
                "type": "text_analysis",
                "description": f"Model classified text as {classification} with {confidence:.2%} confidence",
                "severity": severity,
                "model_id": MODEL_ID,
                "raw_label": label,
            }
        ],
    }
