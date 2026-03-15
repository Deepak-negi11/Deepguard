from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, VerificationRequest
from app.schemas import NewsVerifyRequest, StoredJob, TaskQueuedResponse
from app.services.job_store import job_store
from app.services.storage import store_upload
from app.services.verification import VerificationTaskInput, run_request_analysis

router = APIRouter()
settings = get_settings()

ALLOWED_UPLOADS = {
    "video": {
        "extensions": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
        "content_types": {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"},
    },
    "audio": {
        "extensions": {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"},
        "content_types": {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/aac", "audio/flac", "audio/ogg"},
    },
}


def _content_signature_matches(*, mode: str, extension: str, content: bytes) -> bool:
    if mode == "video":
        if extension in {".mp4", ".mov", ".m4v"}:
            return len(content) >= 12 and content[4:8] == b"ftyp"
        if extension == ".avi":
            return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"AVI "
        if extension in {".mkv", ".webm"}:
            return content.startswith(b"\x1A\x45\xDF\xA3")
        return True

    if extension == ".wav":
        return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WAVE"
    if extension == ".mp3":
        return content.startswith(b"ID3") or (len(content) >= 2 and content[0] == 0xFF and (content[1] & 0xE0) == 0xE0)
    if extension == ".m4a":
        return len(content) >= 12 and content[4:8] == b"ftyp"
    if extension == ".aac":
        return len(content) >= 2 and content[0] == 0xFF and (content[1] & 0xF0) == 0xF0
    if extension == ".flac":
        return content.startswith(b"fLaC")
    if extension == ".ogg":
        return content.startswith(b"OggS")
    return True


def _safe_file_name(file_name: str | None) -> str:
    if not file_name:
        return "upload.bin"
    return Path(file_name).name or "upload.bin"


def _validate_upload(*, mode: str, file_name: str, content_type: str | None, content: bytes) -> tuple[str, str | None]:
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

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
        if task_input.request_type == "video":
            from app.tasks.video_tasks import analyze_video_task

            analyze_video_task.apply_async(
                kwargs={
                    "request_id": task_input.request_id,
                    "file_name": task_input.file_name,
                    "content_type": task_input.content_type,
                    "file_path": task_input.file_path,
                },
                task_id=task_input.task_id,
            )
            return

        if task_input.request_type == "audio":
            from app.tasks.audio_tasks import analyze_audio_task

            analyze_audio_task.apply_async(
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


@router.post("/video", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
async def verify_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskQueuedResponse:
    content = await file.read()
    safe_name, content_type = _validate_upload(mode="video", file_name=file.filename, content_type=file.content_type, content=content)

    request = VerificationRequest(user_id=user.id, request_type="video", status="pending", file_name=safe_name)
    db.add(request)
    db.commit()
    db.refresh(request)
    task_id = request.id
    file_path = store_upload(request_id=request.id, request_type="video", file_name=safe_name, content=content)
    job_store.create(StoredJob(task_id=task_id, request_id=request.id, status="queued", progress=5, current_step="Video queued"))
    _dispatch_verification(
        background_tasks=background_tasks,
        task_input=VerificationTaskInput(
            task_id=task_id,
            request_id=request.id,
            request_type="video",
            file_name=safe_name,
            content_type=content_type,
            file_path=file_path,
        ),
    )
    return TaskQueuedResponse(task_id=task_id, request_id=request.id, status="queued", message="Video queued for analysis")


@router.post("/audio", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
async def verify_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskQueuedResponse:
    content = await file.read()
    safe_name, content_type = _validate_upload(mode="audio", file_name=file.filename, content_type=file.content_type, content=content)

    request = VerificationRequest(user_id=user.id, request_type="audio", status="pending", file_name=safe_name)
    db.add(request)
    db.commit()
    db.refresh(request)
    task_id = request.id
    file_path = store_upload(request_id=request.id, request_type="audio", file_name=safe_name, content=content)
    job_store.create(StoredJob(task_id=task_id, request_id=request.id, status="queued", progress=5, current_step="Audio queued"))
    _dispatch_verification(
        background_tasks=background_tasks,
        task_input=VerificationTaskInput(
            task_id=task_id,
            request_id=request.id,
            request_type="audio",
            file_name=safe_name,
            content_type=content_type,
            file_path=file_path,
        ),
    )
    return TaskQueuedResponse(task_id=task_id, request_id=request.id, status="queued", message="Audio queued for analysis")


@router.post("/news", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
def verify_news(payload: NewsVerifyRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskQueuedResponse:
    if not payload.text and not payload.url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide article text or a URL")

    excerpt = (payload.text or str(payload.url) or "")[:240]
    request = VerificationRequest(user_id=user.id, request_type="news", status="pending", url=str(payload.url) if payload.url else None, payload_excerpt=excerpt)
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
            text=payload.text,
            url=str(payload.url) if payload.url else None,
        ),
    )
    return TaskQueuedResponse(task_id=task_id, request_id=request.id, status="queued", message="News item queued for analysis")
