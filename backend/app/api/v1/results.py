from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import StoredAnalysisPayload, User, VerificationRequest
from app.schemas import AnalysisPayload, TaskResultResponse
from app.services.job_store import job_store

router = APIRouter()


def _status_to_progress(status_value: str) -> tuple[int, str]:
    mapping = {
        "pending": (5, "Awaiting worker pickup"),
        "processing": (45, "Forensic analysis in progress"),
        "completed": (100, "Analysis complete"),
        "failed": (100, "Analysis failed"),
    }
    return mapping.get(status_value, (0, "Unknown status"))


def _is_terminal(status_value: str) -> bool:
    return status_value in {"completed", "failed"}


@router.get("/{task_id}", response_model=TaskResultResponse)
def get_result(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskResultResponse:
    request = db.get(VerificationRequest, task_id)
    if request is None or request.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    job = job_store.get(task_id)
    snapshot = db.query(StoredAnalysisPayload).filter(StoredAnalysisPayload.request_id == request.id).one_or_none()
    persisted_payload = AnalysisPayload.model_validate(snapshot.payload) if snapshot else None

    # Persisted database state is authoritative once the request has left the queue.
    if _is_terminal(request.status):
        if job is not None:
            job_store.delete(task_id)
        progress, step = _status_to_progress(request.status)
        return TaskResultResponse(
            task_id=request.id,
            status=request.status,
            progress=progress,
            current_step=step,
            result=persisted_payload or (job.result if job is not None else None),
        )

    if request.status == "processing":
        progress, step = _status_to_progress(request.status)
        return TaskResultResponse(
            task_id=request.id,
            status=request.status,
            progress=job.progress if job is not None and job.status == "processing" else progress,
            current_step=job.current_step if job is not None and job.status == "processing" else step,
            result=job.result if job is not None else None,
        )

    if job is not None:
        return TaskResultResponse(
            task_id=job.task_id,
            status=job.status,
            progress=job.progress,
            current_step=job.current_step,
            result=job.result,
        )

    progress, step = _status_to_progress(request.status)
    return TaskResultResponse(
        task_id=request.id,
        status=request.status,
        progress=progress,
        current_step=step,
        result=persisted_payload,
    )
