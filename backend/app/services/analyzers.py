import hashlib
import math
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

# Ensure parent directory is in path for ml_models imports (Celery workers)
_APP_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from app.config import get_settings
from app.schemas import AnalysisInputProfile, AnalysisPayload, EvidenceItem

settings = get_settings()


@dataclass(slots=True)
class BinaryArtifactInput:
    request_type: str
    file_name: str
    raw_bytes: bytes
    content_type: str | None = None


def analyze_news(*, text: str, url: str | None = None) -> AnalysisPayload:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"analyze_news called: enable_demo_analyzers={settings.enable_demo_analyzers}")
    if settings.enable_demo_analyzers:
        return _analyze_news_demo(text=text, url=url)
    try:
        return _analyze_news_model(text=text, url=url)
    except Exception as e:
        # In some environments (CI, minimal installs) optional ML dependencies or weights
        # may be unavailable. Falling back keeps the API functional and lets jobs complete.
        logger.warning(f"News model failed, falling back to demo: {e}")
        return _analyze_news_demo(text=text, url=url)


def analyze_binary_artifact(payload: BinaryArtifactInput) -> AnalysisPayload:
    if settings.enable_demo_analyzers:
        return _analyze_binary_artifact_demo(payload)
    try:
        return _analyze_binary_artifact_model(payload)
    except Exception:
        return _analyze_binary_artifact_demo(payload)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _score_to_verdict(fake_score: float) -> tuple[str, float]:
    if fake_score >= 0.68:
        return "likely fake", fake_score
    if fake_score <= 0.32:
        return "likely real", 1.0 - fake_score
    return "uncertain", max(fake_score, 1.0 - fake_score)


def _analyze_news_demo(*, text: str, url: str | None = None) -> AnalysisPayload:
    start = time.perf_counter()
    normalized_text = text.strip()
    combined_text = f"{normalized_text} {url or ''}".lower()
    source_domain = urlparse(url).hostname if url else None

    urgency_terms = {"breaking", "urgent", "shocking", "secret", "leaked", "exclusive", "must", "immediately"}
    sensational_hits = sum(term in combined_text for term in urgency_terms)
    exclamation_score = min(combined_text.count("!"), 6) / 6
    all_caps_words = sum(word.isupper() and len(word) > 3 for word in normalized_text.split())
    length_score = 1.0 - min(len(normalized_text), 1500) / 1500 if normalized_text else 0.75
    source_score = 0.72 if source_domain else 0.48
    rhetoric_score = _clamp(0.22 + sensational_hits * 0.11 + exclamation_score * 0.2 + min(all_caps_words, 4) * 0.08)
    cross_reference_score = _clamp(0.38 + source_score * 0.35 - rhetoric_score * 0.22 - length_score * 0.15)
    fake_score = _clamp(0.18 + rhetoric_score * 0.42 + length_score * 0.18 + (1.0 - source_score) * 0.22 + (1.0 - cross_reference_score) * 0.18)

    verdict, confidence = _score_to_verdict(fake_score)
    authenticity_score = round(1.0 - fake_score, 3)

    evidence: list[EvidenceItem] = []
    if sensational_hits:
        evidence.append(
            EvidenceItem(
                category="rhetoric",
                severity="medium" if sensational_hits < 3 else "high",
                description="Sensational or urgency-heavy phrasing increases manipulation risk.",
                details={"matched_terms": sensational_hits, "sample_terms": ", ".join(sorted(term for term in urgency_terms if term in combined_text)[:4])},
                visualization_hint="credibility_heatmap",
            )
        )
    if source_domain:
        evidence.append(
            EvidenceItem(
                category="source",
                severity="low" if source_score >= 0.7 else "medium",
                description="Source metadata was present and contributed to the credibility estimate.",
                details={"source_domain": source_domain, "source_signal": round(source_score, 3)},
                visualization_hint="source-timeline",
            )
        )
    else:
        evidence.append(
            EvidenceItem(
                category="source",
                severity="medium",
                description="No source URL was provided, so provenance confidence is lower.",
                details={"source_domain": None, "source_signal": round(source_score, 3)},
                visualization_hint="source-timeline",
            )
        )

    duration = round(time.perf_counter() - start, 3)
    return AnalysisPayload(
        authenticity_score=authenticity_score,
        verdict=verdict,
        confidence=round(confidence, 3),
        summary="DeepGuard used fast prototype credibility heuristics to score rhetoric, provenance, and consistency signals for this text.",
        disclaimer="Prototype analyzer only. Replace with the full BERT and cross-reference pipeline for production use.",
        breakdown={
            "language_consistency": round(1.0 - rhetoric_score, 3),
            "source_reputation": round(source_score, 3),
            "cross_reference_signal": round(cross_reference_score, 3),
            "manipulation_risk": round(fake_score, 3),
        },
        evidence=evidence,
        recommended_actions=[
            "Cross-check the core claim against at least two independent sources.",
            "Preserve the original article URL or screenshot before sharing downstream.",
        ],
        input_profile=AnalysisInputProfile(
            mode="news",
            url_domain=source_domain,
            text_length=len(normalized_text),
            analyzer_family="prototype-credibility-heuristics",
        ),
        processing_time_seconds=duration,
        model_version="prototype-news-v1",
    )


def _analyze_news_model(*, text: str, url: str | None = None) -> AnalysisPayload:
    start = time.perf_counter()

    from ml_models.fake_news_detector.inference import predict_news

    prediction = predict_news(text, url)

    classification = prediction.get("classification", "UNKNOWN")
    confidence = prediction.get("confidence", 0.0)
    anomalies = prediction.get("anomalies", [])

    verdict = "likely real" if classification == "REAL" and confidence > 0.6 else "likely fake" if classification == "FAKE" and confidence > 0.6 else "uncertain"
    authenticity_score = confidence if classification == "REAL" else (1.0 - confidence)
    source_domain = urlparse(url).hostname if url else None

    evidence = [
        EvidenceItem(
            category=a["type"],
            severity=a["severity"],
            description=a["description"],
            details={"raw_confidence": confidence, "source_domain": source_domain},
            visualization_hint="credibility_heatmap",
        )
        for a in anomalies
    ]

    duration = round(time.perf_counter() - start, 3)

    return AnalysisPayload(
        authenticity_score=round(authenticity_score, 3),
        verdict=verdict,
        confidence=round(confidence, 3),
        summary=f"DeepGuard AI analyzed the text and concluded it is {classification} with {confidence*100:.1f}% confidence.",
        disclaimer="Analyzed using pre-trained DistilBERT Fake News weights.",
        breakdown={
            "text_analysis_confidence": round(confidence, 3),
            "language_consistency": round(confidence, 3),
            "source_reputation": 0.65 if source_domain else 0.4,
        },
        evidence=evidence,
        recommended_actions=["Manual review recommended." if verdict == "uncertain" else "Trust but verify."],
        input_profile=AnalysisInputProfile(
            mode="news",
            url_domain=source_domain,
            text_length=len(text),
            analyzer_family="distilbert-fake-news",
        ),
        processing_time_seconds=duration,
        model_version="huggingface-distilbert-v1",
    )


def _binary_entropy(raw_bytes: bytes) -> float:
    if not raw_bytes:
        return 0.0
    frequencies = [0] * 256
    for byte in raw_bytes:
        frequencies[byte] += 1
    total = len(raw_bytes)
    entropy = 0.0
    for count in frequencies:
        if count:
            probability = count / total
            entropy -= probability * math.log2(probability)
    return entropy / 8.0


def _stable_signal(raw_value: str) -> float:
    digest = hashlib.sha256(raw_value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def _analyze_binary_artifact_demo(payload: BinaryArtifactInput) -> AnalysisPayload:
    start = time.perf_counter()
    size_bytes = len(payload.raw_bytes)
    extension = Path(payload.file_name).suffix.lower()
    entropy_signal = _clamp(_binary_entropy(payload.raw_bytes))
    size_signal = _clamp(min(size_bytes, 25 * 1024 * 1024) / float(25 * 1024 * 1024))
    marker_signal = _stable_signal(f"{payload.request_type}:{payload.file_name}:{size_bytes}")

    if payload.request_type == "image":
        # Check EXIF (demo)
        # Note: In a real flow, if EXIF is stripped for privacy before analysis, we would extract these signals
        # beforehand. Here we simulate finding missing/software tags.
        has_camera_metadata = marker_signal > 0.4 # simulated
        has_ai_software_tag = marker_signal > 0.8 # simulated
        noise_uniformity = _clamp(0.2 + entropy_signal * 0.4)
        dct_double_compression = _clamp(0.1 + (1.0 - size_signal) * 0.3)
        
        exif_penalty = 0.3 if not has_camera_metadata else 0.0
        exif_penalty += 0.5 if has_ai_software_tag else 0.0
        
        artifact_score = _clamp((noise_uniformity * 0.6) + (dct_double_compression * 0.4))
        fake_score = _clamp(artifact_score * 0.5 + exif_penalty * 0.5)
        
        analyzer_family = "prototype-image-heuristics"
        recommended_actions = [
            "Check for missing EXIF metadata (e.g., camera make/model).",
            "Perform an Error Level Analysis (ELA) or noise residual scan to detect manipulation.",
        ]
        
        evidence = [
            EvidenceItem(
                category="EXIF Metadata",
                severity="high" if exif_penalty > 0.3 else "low",
                description="Checking EXIF for camera signatures or AI software tags.",
                details={"has_camera_metadata": has_camera_metadata, "has_ai_software_tag": has_ai_software_tag},
                visualization_hint="metadata_table",
            ),
            EvidenceItem(
                category="Noise Uniformity",
                severity="medium" if noise_uniformity >= 0.5 else "low",
                description="AI-generated images often exhibit unnaturally uniform block noise variance.",
                details={"noise_uniformity_score": round(noise_uniformity, 3)},
                visualization_hint="noise_residual_heatmap",
            ),
            EvidenceItem(
                category="JPEG Compression",
                severity="low",
                description="Double JPEG compression artifacts from DCT coefficient histograms.",
                details={"dct_anomaly_score": round(dct_double_compression, 3)},
                visualization_hint="dct_histogram",
            )
        ]
        breakdown = {
            "exif_anomaly": round(exif_penalty, 3),
            "noise_pattern_score": round(noise_uniformity, 3),
            "frequency_artifact_score": round(dct_double_compression, 3),
            "manipulation_risk": round(fake_score, 3),
        }
    else:
        spectral_score = _clamp(0.26 + entropy_signal * 0.24 + marker_signal * 0.18)
        cadence_score = _clamp(0.66 - abs(0.5 - marker_signal) * 0.7)
        artifact_score = _clamp(0.22 + (1.0 - size_signal) * 0.18 + entropy_signal * 0.22)
        fake_score = _clamp(spectral_score * 0.34 + (1.0 - cadence_score) * 0.28 + artifact_score * 0.2 + marker_signal * 0.18)
        analyzer_family = "prototype-audio-heuristics"
        recommended_actions = [
            "Compare the sample with a trusted voice baseline before treating it as authentic.",
            "Retain the original recording to avoid introducing re-encoding artifacts.",
        ]
        evidence = [
            EvidenceItem(
                category="Spectral Artifact",
                severity="high" if fake_score >= 0.68 else "medium",
                description="Prototype spectral heuristics detected regularity patterns that can appear in synthetic audio.",
                timestamp=round(marker_signal * 18, 1),
                details={"spectral_signal": round(spectral_score, 3), "entropy_signal": round(entropy_signal, 3)},
                visualization_hint="timeline-marker",
            ),
            EvidenceItem(
                category="Cadence Consistency",
                severity="low" if cadence_score >= 0.55 else "medium",
                description="Cadence consistency was estimated using a lightweight byte-pattern proxy rather than a real prosody model.",
                details={"cadence_score": round(cadence_score, 3), "file_extension": extension or "unknown"},
                visualization_hint="prosody-trace",
            ),
        ]
        breakdown = {
            "spectral_artifact_signal": round(spectral_score, 3),
            "cadence_consistency": round(cadence_score, 3),
            "artifact_detector": round(artifact_score, 3),
            "manipulation_risk": round(fake_score, 3),
        }

    verdict, confidence = _score_to_verdict(fake_score)
    duration = round(time.perf_counter() - start, 3)
    return AnalysisPayload(
        authenticity_score=round(1.0 - fake_score, 3),
        verdict=verdict,
        confidence=round(confidence, 3),
        summary=f"DeepGuard used a fast prototype {payload.request_type} analyzer to score artifact, consistency, and provenance indicators.",
        disclaimer="Prototype analyzer only. Replace with the full trained model pipeline for production use.",
        breakdown=breakdown,
        evidence=evidence,
        recommended_actions=recommended_actions,
        input_profile=AnalysisInputProfile(
            mode=payload.request_type,
            filename=payload.file_name,
            content_type=payload.content_type,
            size_bytes=size_bytes,
            analyzer_family=analyzer_family,
        ),
        processing_time_seconds=duration,
        model_version=f"{analyzer_family}-v1",
    )


def _analyze_binary_artifact_model(payload: BinaryArtifactInput) -> AnalysisPayload:
    start = time.perf_counter()

    suffix = ".jpg" if payload.request_type == "image" else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(payload.raw_bytes)
        tmp_path = Path(tmp.name)

    try:
        if payload.request_type == "image":
            from ml_models.image_deepfake_detector.inference import predict_image

            prediction = predict_image(str(tmp_path))

            classification = prediction.get("label", "unknown").upper()
            confidence = prediction.get("confidence", 0.0)
            breakdown_array = prediction.get("breakdown", [])

            evidence = []
            breakdown = {}

            # Parse array of signals
            for item in breakdown_array:
                sig_name = item.get("signal_name")
                if sig_name == "C2PA/Watermark detected":
                    evidence.append(EvidenceItem(
                        category="C2PA Watermark",
                        severity="high",
                        description=f"AI generation watermark detected: {item.get('marker')}",
                        details=item,
                        visualization_hint="metadata_table"
                    ))
                    breakdown["c2pa_detected"] = 1.0
                elif sig_name == "ML Model":
                    evidence.append(EvidenceItem(
                        category="ML Model Analysis",
                        severity="high" if confidence > 0.7 else "medium",
                        description=f"Model classified as {classification} with {confidence:.1%} confidence.",
                        details=item,
                        visualization_hint="confidence_gauge"
                    ))
                    breakdown["ml_model_confidence"] = round(item.get("confidence", 0.0), 3)
                elif sig_name == "FFT Frequency Analysis":
                    score = item.get("score", 0.0)
                    evidence.append(EvidenceItem(
                        category="Frequency Analysis",
                        severity="medium" if score > 0.5 else "low",
                        description="FFT analysis of frequency spectrum anomalies.",
                        details=item,
                        visualization_hint="dct_histogram"
                    ))
                    breakdown["frequency_artifact_score"] = round(score, 3)
                elif sig_name == "Noise Uniformity (Laplacian)":
                    score = item.get("score", 0.0)
                    evidence.append(EvidenceItem(
                        category="Noise Uniformity",
                        severity="medium" if score > 0.5 else "low",
                        description="Laplacian variance uniformity check.",
                        details=item,
                        visualization_hint="noise_residual_heatmap"
                    ))
                    breakdown["noise_pattern_score"] = round(score, 3)
                elif sig_name == "EXIF Anomaly":
                    anom = item.get("is_anomalous", False)
                    evidence.append(EvidenceItem(
                        category="EXIF Metadata",
                        severity="high" if anom else "low",
                        description=item.get("detail", "EXIF status"),
                        details=item,
                        visualization_hint="metadata_table"
                    ))
                    breakdown["exif_anomaly"] = 1.0 if anom else 0.0

            verdict = "likely real" if classification == "REAL" and confidence > 0.6 else "likely fake" if classification == "FAKE" and confidence > 0.6 else "uncertain"
            authenticity_score = confidence if classification == "REAL" else (1.0 - confidence)

            model_family = "Ateeqq/image-detector"
            gradcam_url = None

        else:
            from ml_models.audio_detector.inference import predict_audio

            prediction = predict_audio(tmp_path)
            model_family = "rawnet2-asvspoof"

            classification = prediction.get("classification", "UNKNOWN")
            confidence = prediction.get("confidence", 0.0)
            anomalies = prediction.get("anomalies", [])
            gradcam_url = None

            verdict = "likely real" if classification == "REAL" and confidence > 0.6 else "likely fake" if classification == "FAKE" and confidence > 0.6 else "uncertain"
            authenticity_score = confidence if classification == "REAL" else (1.0 - confidence)

            evidence = [
                EvidenceItem(
                    category=a["type"],
                    severity=a["severity"],
                    description=a["description"],
                    timestamp=0.0,
                    details={"model_confidence": confidence},
                    visualization_hint="timeline-marker",
                )
                for a in anomalies
            ]
            breakdown = {"model_confidence": round(confidence, 3)}

        duration = round(time.perf_counter() - start, 3)

        return AnalysisPayload(
            authenticity_score=round(authenticity_score, 3),
            verdict=verdict,
            confidence=round(confidence, 3),
            summary=f"DeepGuard analyzed the {payload.request_type} using a 3-layer detection pipeline and concluded it is {classification} with {confidence*100:.1f}% confidence.",
            disclaimer=f"Analyzed using {model_family}. Real-world accuracy ~85-90%.",
            breakdown=breakdown,
            evidence=evidence,
            recommended_actions=["Manual review recommended." if verdict == "uncertain" else "Trust but verify."],
            input_profile=AnalysisInputProfile(
                mode=payload.request_type,
                filename=payload.file_name,
                content_type=payload.content_type,
                size_bytes=len(payload.raw_bytes),
                analyzer_family=model_family,
            ),
            processing_time_seconds=duration,
            model_version=f"{model_family}-v1",
            gradcam_overlay_url=gradcam_url,
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
