from __future__ import annotations

from app.services.verification import VerificationTaskInput, run_request_analysis
from app.tasks.celery_app import celery_app


@celery_app.task(name="deepguard.news.analyze")
def analyze_news_task(*, request_id: str, text: str | None = None, url: str | None = None) -> None:
    run_request_analysis(
        VerificationTaskInput(
            task_id=request_id,
            request_id=request_id,
            request_type="news",
            text=text,
            url=url,
        )
    )
