from __future__ import annotations

import logging
from typing import Any

import piexif
from PIL import Image

from app.services.verification import VerificationTaskInput, run_request_analysis
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def strip_and_save(path: str) -> str:
    """Strips EXIF data (like GPS coordinates) before analysis for privacy."""
    try:
        img = Image.open(path)
        # Load existing exif, if it fails or doesn't exist, we just save without it
        exif_dict = piexif.load(img.info.get("exif", b"")) if "exif" in img.info else {}
        
        # In a real scenario, you might preserve specific tags needed for heuristic analysis,
        # but here we wipe it to an empty dict as requested in the plan.
        safe_exif = piexif.dump({})
        
        # Save the image, overwriting the original file
        img.save(path, exif=safe_exif)
        logger.info(f"Stripped EXIF metadata from {path}")
    except Exception as exc:
        logger.warning(f"Failed to strip EXIF from {path}: {exc}")
    
    return path


@celery_app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=300,
    time_limit=360,
    autoretry_for=(Exception,),
    retry_backoff=True,
    name="deepguard.image.analyze"
)
def analyze_image_task(self: Any, *, request_id: str, file_name: str, content_type: str | None = None, file_path: str | None = None) -> None:

    
    run_request_analysis(
        VerificationTaskInput(
            task_id=request_id,
            request_id=request_id,
            request_type="image",
            file_name=file_name,
            content_type=content_type,
            file_path=file_path,
        )
    )
