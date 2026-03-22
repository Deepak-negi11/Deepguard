import sys
from pathlib import Path

from celery import Celery

from app.config import get_settings

# Ensure /app is in Python path for ml_models imports
_APP_ROOT = Path(__file__).resolve().parent.parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

settings = get_settings()
celery_app = Celery(
    "deepguard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.image_tasks",
        "app.tasks.news_tasks",
        "app.tasks.audio_tasks",
    ]
)
