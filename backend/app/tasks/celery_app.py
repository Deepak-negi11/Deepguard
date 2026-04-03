import logging
import sys
from pathlib import Path

from celery import Celery
from celery.signals import worker_init

from app.config import get_settings

# Ensure /app is in Python path for ml_models imports
_APP_ROOT = Path(__file__).resolve().parent.parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

settings = get_settings()
logger = logging.getLogger(__name__)
celery_app = Celery(
    "deepguard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.image_tasks",
        "app.tasks.news_tasks",
    ]
)


@worker_init.connect
def warm_models_on_worker_startup(**_: object) -> None:
    if settings.enable_demo_analyzers or not settings.warm_news_model_on_startup:
        return

    try:
        from ml_models.fake_news_detector.inference import get_news_model_source, warm_news_model

        if warm_news_model():
            logger.info("News model warm-up complete (%s).", get_news_model_source())
        else:
            logger.warning("News model warm-up did not complete successfully.")
    except Exception as exc:  # pragma: no cover - defensive startup logging
        logger.warning("News model warm-up failed during worker startup: %s", exc)
