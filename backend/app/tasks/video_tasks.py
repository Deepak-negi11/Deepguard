from __future__ import annotations

from app.services.verification import VerificationTaskInput, run_request_analysis
from app.tasks.celery_app import celery_app


@celery_app.task(name="deepguard.video.analyze")
def analyze_video_task(*, request_id: str, file_name: str, content_type: str | None = None, file_path: str | None = None) -> None:
    run_request_analysis(
        VerificationTaskInput(
            task_id=request_id,
            request_id=request_id,
            request_type="video",
            file_name=file_name,
            content_type=content_type,
            file_path=file_path,
        )
    )
