from celery import Celery

from app.config import get_settings

settings = get_settings()
celery_app = Celery(
    "deepguard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.video_tasks",
        "app.tasks.news_tasks",
        "app.tasks.audio_tasks",
    ]
)
