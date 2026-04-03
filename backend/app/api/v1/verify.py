from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, VerificationRequest
from app.schemas import NewsVerifyRequest, StoredJob, TaskQueuedResponse
from app.services.job_store import job_store
from app.services.news_ingestion import resolve_news_input
from app.services.storage import store_upload_stream
from app.services.verification import VerificationTaskInput, run_request_analysis

router = APIRouter()
settings = get_settings()

ALLOWED_UPLOADS = {
    "image": {
        "extensions": {".jpg", ".jpeg", ".png", ".webp"},
        "content_types": {"image/jpeg", "image/png", "image/webp"},
    },
}


def _content_signature_matches(*, mode: str, extension: str, content: bytes) -> bool:
    if mode == "image":
        if extension in {".jpg", ".jpeg"}:
            return content.startswith(b"\xff\xd8")
        if extension == ".png":
            return content.startswith(b"\x89PNG\r\n\x1a\n")
        if extension == ".webp":
            return content.startswith(b"RIFF") and content[8:12] == b"WEBP"
        return True
    return True


def _safe_file_name(file_name: str | None) -> str:
    if not file_name:
        return "upload.bin"
    return Path(file_name).name or "upload.bin"


def _validate_upload(*, mode: str, file_name: str, content_type: str | None, content: bytes) -> tuple[str, str | None]:
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    if mode not in ALLOWED_UPLOADS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported {mode} upload mode",
        )

    max_upload_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Upload exceeds the {settings.max_upload_mb} MB limit",
        )

    safe_name = _safe_file_name(file_name)
    extension = Path(safe_name).suffix.lower()
    allowed = ALLOWED_UPLOADS[mode]
    if extension not in allowed["extensions"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported {mode} file type: {extension or 'missing extension'}",
        )

    if not _content_signature_matches(mode=mode, extension=extension, content=content):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Uploaded {mode} file signature does not match extension {extension}",
        )

    normalized_content_type = content_type or None
    if normalized_content_type and normalized_content_type.lower() not in allowed["content_types"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported {mode} content type: {normalized_content_type}",
        )

    return safe_name, normalized_content_type


def _dispatch_verification(*, background_tasks: BackgroundTasks, task_input: VerificationTaskInput) -> None:
    if settings.enable_celery_workers:
        if task_input.request_type == "image":
            from app.tasks.image_tasks import analyze_image_task

            analyze_image_task.apply_async(
                kwargs={
                    "request_id": task_input.request_id,
                    "file_name": task_input.file_name,
                    "content_type": task_input.content_type,
                    "file_path": task_input.file_path,
                },
                task_id=task_input.task_id,
            )
            return

        from app.tasks.news_tasks import analyze_news_task

        analyze_news_task.apply_async(
            kwargs={
                "request_id": task_input.request_id,
                "text": task_input.text,
                "url": task_input.url,
            },
            task_id=task_input.task_id,
        )
        return

    background_tasks.add_task(run_request_analysis, task_input)


MAX_IMAGE_SIZE_MB = 10

@router.post("/image", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
def verify_image(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskQueuedResponse:  # noqa: B008
    if file.size and file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds the {MAX_IMAGE_SIZE_MB} MB limit",
        )

    # Peek for validation without loading full payload.
    head = file.file.read(4096)
    if not head:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    file.file.seek(0)
    safe_name, content_type = _validate_upload(mode="image", file_name=file.filename, content_type=file.content_type, content=head)

    db_request = VerificationRequest(user_id=user.id, request_type="image", status="pending", file_name=safe_name)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    task_id = db_request.id

    max_upload_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
    try:
        file_path, _ = store_upload_stream(
            request_id=db_request.id,
            request_type="image",
            file_name=safe_name,
            source=file.file,
            max_bytes=max_upload_bytes,
        )
    except ValueError as exc:
        if str(exc) == "upload_too_large":
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload exceeds the {MAX_IMAGE_SIZE_MB} MB limit",
            ) from exc
        raise

    job_store.create(StoredJob(task_id=task_id, request_id=db_request.id, status="queued", progress=5, current_step="Image queued"))
    _dispatch_verification(
        background_tasks=background_tasks,
        task_input=VerificationTaskInput(
            task_id=task_id,
            request_id=db_request.id,
            request_type="image",
            file_name=safe_name,
            content_type=content_type,
            file_path=file_path,
        ),
    )
    return TaskQueuedResponse(task_id=task_id, request_id=db_request.id, status="queued", message="Image queued for analysis")



@router.post("/news", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
def verify_news(payload: NewsVerifyRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskQueuedResponse:  # noqa: B008
    if not payload.text and not payload.url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide article text or a URL")

    resolved = resolve_news_input(text=payload.text, url=str(payload.url) if payload.url else None)
    if not resolved.text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract article text from the provided URL. Paste article text directly or use a reachable public URL.",
        )

    excerpt = resolved.text[:240]
    request = VerificationRequest(
        user_id=user.id,
        request_type="news",
        status="pending",
        url=resolved.url,
        payload_excerpt=excerpt,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    task_id = request.id
    job_store.create(StoredJob(task_id=task_id, request_id=request.id, status="queued", progress=5, current_step="News article queued"))
    _dispatch_verification(
        background_tasks=background_tasks,
        task_input=VerificationTaskInput(
            task_id=task_id,
            request_id=request.id,
            request_type="news",
            text=resolved.text,
            url=resolved.url,
        ),
    )
    return TaskQueuedResponse(task_id=task_id, request_id=request.id, status="queued", message="News item queued for analysis")
