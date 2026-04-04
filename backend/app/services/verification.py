from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
from app.models import EvidenceItemRecord, StoredAnalysisPayload, User, VerificationRequest, VerificationResult
from app.schemas import AnalysisPayload
from app.services.analyzers import BinaryArtifactInput, analyze_binary_artifact, analyze_news
from app.services.job_store import job_store
from app.services.storage import delete_upload, load_upload_bytes

settings = get_settings()


@dataclass(slots=True)
class VerificationTaskInput:
    task_id: str
    request_id: str
    request_type: str
    text: str | None = None
    url: str | None = None
    file_name: str | None = None
    content_type: str | None = None
    file_path: str | None = None


def _processing_step(request_type: str) -> str:
    return {
        "image": "Extracting features and running patch analysis",
        "news": "Scoring rhetoric, source trust, and cross-reference cues",
    }.get(request_type, "Running forensic analysis")


def run_request_analysis(task_input: VerificationTaskInput) -> None:
    """Execute a verification request and persist the result payload."""

    db = SessionLocal()
    try:
        request = db.get(VerificationRequest, task_input.request_id)
        if request is None:
            return

        request.status = "processing"
        db.commit()
        job_store.update(
            task_input.task_id,
            status="processing",
            progress=45,
            current_step=_processing_step(task_input.request_type),
        )

        if task_input.request_type == "news":
            result_payload = analyze_news(text=task_input.text or "", url=task_input.url)
        else:
            raw_bytes = load_upload_bytes(task_input.file_path) if task_input.file_path else b""
            result_payload = analyze_binary_artifact(
                BinaryArtifactInput(
                    request_type=task_input.request_type,
                    file_name=task_input.file_name or "upload.bin",
                    raw_bytes=raw_bytes,
                    content_type=task_input.content_type,
                )
            )

        _persist_result(db=db, request_id=task_input.request_id, result_payload=result_payload)
        request.status = "completed"
        db.commit()
        # Usage tracking should never flip a successful analysis into a failed job.
        try:
            db.refresh(request)
            user = db.get(User, request.user_id)
            if user is not None:
                user.monthly_usage += 1
                db.commit()
        except Exception:
            db.rollback()
        job_store.update(
            task_input.task_id,
            status="completed",
            progress=100,
            current_step="Analysis complete",
            result=result_payload,
        )
    except Exception as exc:
        import traceback

        traceback.print_exc()
        if request := db.get(VerificationRequest, task_input.request_id):
            request.status = "failed"
            db.commit()
        job_store.update(
            task_input.task_id,
            status="failed",
            progress=100,
            current_step=f"Analysis failed: {exc}",
        )
    finally:
        db.close()
        if settings.delete_uploads_after_processing:
            delete_upload(task_input.file_path)


def _persist_result(*, db, request_id: str, result_payload: AnalysisPayload) -> None:
    # Persist atomically: either all result rows exist or none do.
    with db.begin():
        existing_result = db.scalar(select(VerificationResult).where(VerificationResult.request_id == request_id))
        if existing_result is not None:
            db.delete(existing_result)

        existing_snapshot = db.scalar(
            select(StoredAnalysisPayload).where(StoredAnalysisPayload.request_id == request_id)
        )
        if existing_snapshot is not None:
            db.delete(existing_snapshot)

        result_row = VerificationResult(
            request_id=request_id,
            authenticity_score=result_payload.authenticity_score,
            verdict=result_payload.verdict,
            confidence=result_payload.confidence,
            evidence=[item.model_dump() for item in result_payload.evidence],
            breakdown=result_payload.breakdown,
            processing_time_seconds=result_payload.processing_time_seconds,
            model_version=result_payload.model_version,
        )
        db.add(result_row)
        db.flush()

        for item in result_payload.evidence:
            db.add(
                EvidenceItemRecord(
                    result_id=result_row.id,
                    category=item.category,
                    severity=item.severity,
                    description=item.description,
                    details=item.details,
                    timestamp_in_media=item.timestamp,
                    visualization_hint=item.visualization_hint,
                )
            )

        db.add(
            StoredAnalysisPayload(
                request_id=request_id,
                payload=result_payload.model_dump(),
            )
        )
