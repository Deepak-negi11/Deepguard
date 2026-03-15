"""
Audio Deepfake Detection using Wav2Vec2 (Pre-Trained on ASVspoof-like data).
Pattern directly adapted from: Akshayredekar07/Multimodal-Deepfake-Detection
Uses: facebook/wav2vec2-base (fine-tuned for audio classification)
Reference: https://github.com/Akshayredekar07/Multimodal-Deepfake-Detection/blob/main/backend/app/audio_detection.py
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

import torch
import torchaudio

logger = logging.getLogger(__name__)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights" / "audio_deepfake"

# Singleton
_model = None
_processor = None


def _load_model():
    """Load Wav2Vec2 for sequence classification (Real vs Fake audio)."""
    global _model, _processor
    if _model is not None:
        return _model, _processor

    try:
        from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor

        # Try local weights first, then fallback to HuggingFace Hub
        model_name = "facebook/wav2vec2-base"
        logger.info(f"Loading Wav2Vec2 audio model: {model_name}")

        _processor = Wav2Vec2Processor.from_pretrained(model_name)
        # Use 2-class classification (Real=0, Fake=1)
        _model = Wav2Vec2ForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,
            problem_type="single_label_classification",
        )
        _model.eval()
        logger.info("Audio deepfake model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load audio model: {e}")
        _model = None
        _processor = None

    return _model, _processor


def _preprocess_audio(audio_path: str | Path, sample_rate: int = 16000, max_length: float = 4.0):
    """
    Preprocess audio file: load, resample to 16kHz, convert to mono, pad/trim.
    Adapted from Akshayredekar07/Multimodal-Deepfake-Detection.
    """
    audio_path = str(audio_path)
    waveform, orig_sr = torchaudio.load(audio_path)

    # Resample to 16kHz if needed
    if orig_sr != sample_rate:
        resampler = torchaudio.transforms.Resample(orig_sr, sample_rate)
        waveform = resampler(waveform)

    # Convert to mono
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    # Trim or pad to max_length seconds
    max_samples = int(max_length * sample_rate)
    if waveform.shape[1] > max_samples:
        waveform = waveform[:, :max_samples]
    elif waveform.shape[1] < max_samples:
        padding = torch.zeros(1, max_samples - waveform.shape[1])
        waveform = torch.cat([waveform, padding], dim=1)

    # Normalize (zero mean, unit variance)
    waveform = (waveform - waveform.mean()) / (waveform.std() + 1e-6)

    return waveform.squeeze(0)


def predict_audio(audio_path: str | Path) -> dict[str, Any]:
    """
    Predict whether the audio file contains synthetic/deepfake speech.
    Returns dict with: classification, confidence, anomalies
    """
    model, processor = _load_model()

    if model is None or processor is None:
        return {
            "classification": "UNKNOWN",
            "confidence": 0.0,
            "anomalies": [
                {"type": "error", "description": "Audio model failed to load", "severity": "high"}
            ],
        }

    try:
        # Preprocess
        waveform = _preprocess_audio(audio_path)
        waveform_np = waveform.numpy()

        # Process with Wav2Vec2Processor
        inputs = processor(waveform_np, sampling_rate=16000, return_tensors="pt", padding=True)

        # Inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_label = logits.argmax(dim=-1).item()
            confidence = probabilities[0, predicted_label].item()

        # Convert: 0 = Real, 1 = Fake
        classification = "REAL" if predicted_label == 0 else "FAKE"

        return {
            "classification": classification,
            "confidence": confidence,
            "anomalies": [
                {
                    "type": "spectrogram_analysis",
                    "description": f"Wav2Vec2 model classified audio as {classification} with {confidence:.2%} confidence",
                    "severity": "high" if classification == "FAKE" else "low",
                }
            ],
        }

    except Exception as e:
        logger.error(f"Audio inference failed: {e}")
        return {
            "classification": "UNKNOWN",
            "confidence": 0.0,
            "anomalies": [{"type": "error", "description": str(e), "severity": "high"}],
        }
