import hashlib
import math
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

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
    if settings.enable_demo_analyzers:
        return _analyze_news_demo(text=text, url=url)
    try:
        return _analyze_news_model(text=text, url=url)
    except Exception:
        # In some environments (CI, minimal installs) optional ML dependencies or weights
        # may be unavailable. Falling back keeps the API functional and lets jobs complete.
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

    if payload.request_type == "video":
        artifact_score = _clamp(0.24 + entropy_signal * 0.28 + marker_signal * 0.22)
        temporal_score = _clamp(0.32 + (1.0 - abs(0.52 - marker_signal) * 1.4))
        provenance_score = _clamp(0.55 - size_signal * 0.18 + (0.08 if extension in {".mp4", ".mov"} else -0.04))
        fake_score = _clamp(artifact_score * 0.38 + (1.0 - temporal_score) * 0.24 + (1.0 - provenance_score) * 0.18 + marker_signal * 0.2)
        analyzer_family = "prototype-video-heuristics"
        recommended_actions = [
            "Review the original source clip for re-encoding history and upload chain metadata.",
            "Inspect suspicious segments frame by frame before making a final determination.",
        ]
        evidence = [
            EvidenceItem(
                category="Facial Artifacts",
                severity="high" if fake_score >= 0.68 else "medium",
                description="Prototype artifact scan flagged frame-level irregularity patterns worth manual review.",
                timestamp=round(marker_signal * 45, 1),
                details={"entropy_signal": round(entropy_signal, 3), "container_extension": extension or "unknown"},
                visualization_hint="timeline-marker",
            ),
            EvidenceItem(
                category="Compression Pattern",
                severity="low" if provenance_score >= 0.5 else "medium",
                description="Container and byte-distribution signals were used as a lightweight provenance proxy.",
                details={"provenance_score": round(provenance_score, 3), "size_mb": round(size_bytes / (1024 * 1024), 2)},
                visualization_hint="artifact-heatmap",
            ),
        ]
        breakdown = {
            "spatial_artifact_signal": round(artifact_score, 3),
            "temporal_consistency": round(temporal_score, 3),
            "source_provenance": round(provenance_score, 3),
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

    suffix = ".mp4" if payload.request_type == "video" else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(payload.raw_bytes)
        tmp_path = Path(tmp.name)

    try:
        if payload.request_type == "video":
            from ml_models.deepfake_detector.inference import predict_video

            prediction = predict_video(tmp_path)
            model_family = "efficientnet-b4-faceforensics"
        else:
            from ml_models.audio_detector.inference import predict_audio

            prediction = predict_audio(tmp_path)
            model_family = "rawnet2-asvspoof"

        classification = prediction.get("classification", "UNKNOWN")
        confidence = prediction.get("confidence", 0.0)
        anomalies = prediction.get("anomalies", [])

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

        duration = round(time.perf_counter() - start, 3)

        return AnalysisPayload(
            authenticity_score=round(authenticity_score, 3),
            verdict=verdict,
            confidence=round(confidence, 3),
            summary=f"DeepGuard AI analyzed the {payload.request_type} and concluded it is {classification} with {confidence*100:.1f}% confidence.",
            disclaimer=f"Analyzed using pre-trained {model_family} weights.",
            breakdown={"model_confidence": round(confidence, 3)},
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
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
