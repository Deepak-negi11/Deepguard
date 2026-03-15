import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from app.schemas import AnalysisInputProfile, AnalysisPayload, EvidenceItem


@dataclass(slots=True)
class BinaryArtifactInput:
    request_type: str
    file_name: str
    raw_bytes: bytes
    content_type: str | None = None


def analyze_news(*, text: str, url: str | None = None) -> AnalysisPayload:
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


def analyze_binary_artifact(payload: BinaryArtifactInput) -> AnalysisPayload:
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
