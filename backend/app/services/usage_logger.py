from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import ApiUsage


def log_api_usage(
    *,
    db: Session,
    endpoint: str,
    response_time_ms: float | None,
    status_code: int | None,
    user_id: int | None = None,
    error_message: str | None = None,
) -> None:
    """Persist a lightweight API usage record."""

    db.add(
        ApiUsage(
            user_id=user_id,
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            error_message=error_message,
        )
    )
    db.commit()
