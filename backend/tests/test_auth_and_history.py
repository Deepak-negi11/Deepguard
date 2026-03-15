from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import BackgroundTasks, HTTPException

from app.api.v1.auth import login, register
from app.api.v1.history import get_history
from app.api.v1.results import get_result
from app.api.v1.verify import _validate_upload, verify_news
from app.database import Base, SessionLocal, engine
from app.models import ApiUsage, User
from app.schemas import LoginRequest, NewsVerifyRequest, RegisterRequest
from app.services.job_store import job_store
from app.services.usage_logger import log_api_usage


@pytest.fixture(autouse=True)
def reset_database() -> None:
    job_store.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    job_store.clear()
    Base.metadata.drop_all(bind=engine)


def _run_background_tasks(background_tasks: BackgroundTasks) -> None:
    for task in background_tasks.tasks:
        task.func(*task.args, **task.kwargs)


def _load_user(user_id: int) -> User:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        assert user is not None
        db.expunge(user)
        return user
    finally:
        db.close()


def test_register_login_and_history_flow() -> None:
    email = f"tester-{uuid4()}@example.com"

    db = SessionLocal()
    try:
        registered = register(RegisterRequest(email=email, password="strongpass123"), db)
        logged_in = login(LoginRequest(email=email, password="strongpass123"), db)
        user = db.get(User, registered.user_id)
        assert user is not None

        history = get_history(db=db, user=user)
    finally:
        db.close()

    assert registered.email == email
    assert logged_in.user_id == registered.user_id
    assert history.total >= 0


def test_news_verification_returns_rich_analysis_payload() -> None:
    email = f"news-{uuid4()}@example.com"

    db = SessionLocal()
    try:
        registered = register(RegisterRequest(email=email, password="strongpass123"), db)
        user = db.get(User, registered.user_id)
        assert user is not None

        background_tasks = BackgroundTasks()
        queued = verify_news(
            NewsVerifyRequest(
                url="https://example.com/story",
                text="Breaking exclusive leaked report claims a secret urgent event is unfolding right now.",
            ),
            background_tasks=background_tasks,
            db=db,
            user=user,
        )
        assert queued.status == "queued"
        _run_background_tasks(background_tasks)

        result = get_result(queued.task_id, db=db, user=user)
    finally:
        db.close()

    assert result.status == "completed"
    assert result.result is not None
    payload = result.result
    assert payload.summary
    assert payload.disclaimer
    assert payload.recommended_actions
    assert payload.input_profile.mode == "news"
    assert "language_consistency" in payload.breakdown
    assert payload.evidence[0].details


def test_video_verification_rejects_unsupported_file_type() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _validate_upload(
            mode="video",
            file_name="payload.txt",
            content_type="text/plain",
            content=b"not-a-video",
        )

    assert exc_info.value.status_code == 415
    assert "Unsupported video" in str(exc_info.value.detail)


def test_results_endpoint_falls_back_to_persisted_payload_when_job_store_is_empty() -> None:
    email = f"fallback-{uuid4()}@example.com"

    db = SessionLocal()
    try:
        registered = register(RegisterRequest(email=email, password="strongpass123"), db)
        user = db.get(User, registered.user_id)
        assert user is not None

        background_tasks = BackgroundTasks()
        queued = verify_news(
            NewsVerifyRequest(text="Neutral report text with enough length to satisfy validation and no dramatic claims."),
            background_tasks=background_tasks,
            db=db,
            user=user,
        )
        _run_background_tasks(background_tasks)

        job_store.clear()
        result = get_result(queued.task_id, db=db, user=user)
    finally:
        db.close()

    assert result.status == "completed"
    assert result.result is not None
    assert result.result.input_profile.mode == "news"


def test_api_usage_logging_records_api_requests() -> None:
    db = SessionLocal()
    try:
        before_count = db.query(ApiUsage).count()
        log_api_usage(
            db=db,
            endpoint="/api/v1/auth/register",
            response_time_ms=18.4,
            status_code=201,
            user_id=None,
        )
        after_count = db.query(ApiUsage).count()
    finally:
        db.close()

    assert after_count > before_count
