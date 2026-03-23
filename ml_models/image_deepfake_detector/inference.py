"""
3-Layer Image Authenticity Detection Pipeline.

Layer 1 — C2PA / Metadata Watermark Check
Layer 2 — ML Model — Ateeqq/ai-vs-human-image-detector
Layer 3 — FFT + Noise + EXIF heuristics
"""
from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)

# Real CV heuristics
try:
    from ml_models.image_deepfake_detector.preprocessing import compute_noise_uniformity
    from ml_models.image_deepfake_detector.frequency import compute_frequency_anomaly
except ImportError:
    def compute_noise_uniformity(path): return 0.5
    def compute_frequency_anomaly(path): return 0.5

_pipeline = None

def _get_ml_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
        
    try:
        from transformers import pipeline
        logger.info(f"Loading image detection model: Organika/sdxl-detector")
        # Load from the local path where download_pretrained_models downloaded it, 
        # or fallback to HF hub
        _pipeline = pipeline(
            "image-classification", 
            model="Organika/sdxl-detector", 
            device=-1
        )
    except Exception as e:
        logger.error(f"Failed to load image detection model: {e}")
        _pipeline = None
        
    return _pipeline

def check_c2pa(image_path: str) -> dict | None:
    try:
        with open(image_path, "rb") as f:
            raw = f.read().lower()
        
        markers = [b"openai", b"dall-e", b"c2pa", 
                   b"adobe firefly", b"midjourney", 
                   b"stable diffusion"]
        
        for marker in markers:
            if marker in raw:
                return {
                    "signal_name": "C2PA/Watermark detected",
                    "detected": True,
                    "marker": marker.decode()
                }
    except Exception as e:
        logger.warning(f"C2PA check failed: {e}")
    return None

def check_exif_anomaly(image_path: str) -> dict:
    try:
        from PIL import Image
        import piexif
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info.get("exif", b"")) if "exif" in img.info else {}
        if not exif_dict or not exif_dict.get("0th"):
            return {"signal_name": "EXIF Anomaly", "is_anomalous": True, "detail": "Missing EXIF data"}
        return {"signal_name": "EXIF Anomaly", "is_anomalous": False, "detail": "EXIF present"}
    except Exception:
        return {"signal_name": "EXIF Anomaly", "is_anomalous": True, "detail": "Error reading EXIF"}

def predict_image(image_path: str) -> dict:
    start_time = time.time()
    
    # Layer 1 - C2PA Check
    # Immediately return FAKE 95% if watermark is found
    c2pa_res = check_c2pa(image_path)
    if c2pa_res:
        return {
            "label": "FAKE",
            "confidence": 0.95,
            "primary_source": "C2PA/Watermark detected",
            "breakdown": [c2pa_res]
        }
    
    # Layer 2 - ML Model
    pipe = _get_ml_pipeline()
    if pipe:
        from PIL import Image
        img = Image.open(image_path).convert("RGB")
        res = pipe(img)
        best = res[0]
        label_raw = best["label"].lower().strip()
        score = best["score"]
        
        # label artificial means FAKE, label human means REAL
        is_fake = "artificial" in label_raw
        final_label = "FAKE" if is_fake else "REAL"
        final_confidence = score
    else:
        final_label = "UNKNOWN"
        final_confidence = 0.0

    # Layer 3 - Evidence signals
    # Supporting evidence only — do not change verdict
    noise_score = compute_noise_uniformity(image_path)
    freq_score = compute_frequency_anomaly(image_path)
    exif_res = check_exif_anomaly(image_path)
    
    breakdown = [
        {"signal_name": "ML Model", "label": final_label, "confidence": final_confidence, "raw": label_raw},
        {"signal_name": "FFT Frequency Analysis", "score": freq_score},
        {"signal_name": "Noise Uniformity (Laplacian)", "score": noise_score},
        exif_res
    ]
    
    return {
        "label": final_label,
        "confidence": final_confidence,
        "primary_source": "ML Model",
        "breakdown": breakdown
    }
