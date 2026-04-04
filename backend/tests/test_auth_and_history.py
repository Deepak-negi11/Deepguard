from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import BackgroundTasks, HTTPException, Response

from app.api.v1.auth import login, register
from app.api.v1.history import get_history
from app.api.v1.results import get_result
from app.api.v1.system import get_system_status
from app.api.v1.verify import _validate_upload, verify_news
from app.database import SessionLocal
from app.models import ApiUsage, User
from app.schemas import LoginRequest, NewsVerifyRequest, RegisterRequest
from app.services.analyzers import _analyze_news_model
from app.services.job_store import job_store
from app.services.usage_logger import log_api_usage


def _run_background_tasks(background_tasks: BackgroundTasks) -> None:
    for task in background_tasks.tasks:
        task.func(*task.args, **task.kwargs)


def test_register_login_and_history_flow() -> None:
    email = f"tester-{uuid4()}@example.com"

    db = SessionLocal()
    try:
        registered = register(RegisterRequest(email=email, password="strongpass123"), Response(), db)
        logged_in = login(LoginRequest(email=email, password="strongpass123"), Response(), db)
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
        registered = register(RegisterRequest(email=email, password="strongpass123"), Response(), db)
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


def test_news_verification_fetches_public_url_text(monkeypatch) -> None:
    email = f"url-only-{uuid4()}@example.com"

    monkeypatch.setattr(
        "app.api.v1.verify.resolve_news_input",
        lambda **kwargs: type(
            "ResolvedNewsInput",
            (),
            {
                "text": "This article body was fetched from a public URL and has enough content for analysis.",
                "url": "https://example.com/fetched",
                "source_domain": "example.com",
                "fetched_from_url": True,
            },
        )(),
    )

    db = SessionLocal()
    try:
        registered = register(RegisterRequest(email=email, password="strongpass123"), Response(), db)
        user = db.get(User, registered.user_id)
        assert user is not None

        background_tasks = BackgroundTasks()
        queued = verify_news(
            NewsVerifyRequest(url="https://example.com/fetched"),
            background_tasks=background_tasks,
            db=db,
            user=user,
        )
        _run_background_tasks(background_tasks)
        result = get_result(queued.task_id, db=db, user=user)
    finally:
        db.close()

    assert result.status == "completed"
    assert result.result is not None
    assert result.result.input_profile.mode == "news"


def test_analyze_news_model_maps_real_label_to_real_verdict(monkeypatch) -> None:
    monkeypatch.setattr(
        "ml_models.fake_news_detector.inference.predict_news",
        lambda text, url=None: {
            "classification": "REAL",
            "confidence": 0.91,
            "anomalies": [
                {
                    "type": "text_analysis",
                    "severity": "low",
                    "description": "Model classified text as REAL with 91.00% confidence",
                    "model_id": "hamzab/roberta-fake-news-classification",
                    "raw_label": "REAL",
                }
            ],
        },
    )

    result = _analyze_news_model(
        text="BBC reports confirm a factual and current event in a neutral tone.",
        url="https://www.bbc.com/news/articles/example",
    )

    assert result.verdict == "likely real"
    assert result.authenticity_score == pytest.approx(0.91, rel=1e-6)
    assert result.input_profile.analyzer_family == "roberta-fake-news"
    assert result.evidence[0].details["raw_label"] == "REAL"


def test_analyze_news_model_keeps_unknown_predictions_uncertain(monkeypatch) -> None:
    monkeypatch.setattr(
        "ml_models.fake_news_detector.inference.predict_news",
        lambda text, url=None: {
            "classification": "UNKNOWN",
            "confidence": 0.0,
            "anomalies": [
                {
                    "type": "text_analysis",
                    "severity": "medium",
                    "description": "Model classified text as UNKNOWN with 0.00% confidence",
                    "model_id": "hamzab/roberta-fake-news-classification",
                    "raw_label": "LABEL_X",
                }
            ],
        },
    )

    result = _analyze_news_model(text="Short factual text.", url=None)

    assert result.verdict == "uncertain"
    assert result.authenticity_score == pytest.approx(0.5, rel=1e-6)
    assert result.evidence[0].details["model_id"] == "hamzab/roberta-fake-news-classification"


def test_unsupported_upload_mode_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _validate_upload(
            mode="video",
            file_name="payload.txt",
            content_type="text/plain",
            content=b"not-a-video",
        )

    assert exc_info.value.status_code == 415
    assert "Unsupported video upload mode" in str(exc_info.value.detail)


def test_results_endpoint_falls_back_to_persisted_payload_when_job_store_is_empty() -> None:
    email = f"fallback-{uuid4()}@example.com"

    db = SessionLocal()
    try:
        registered = register(RegisterRequest(email=email, password="strongpass123"), Response(), db)
        user = db.get(User, registered.user_id)
        assert user is not None

        background_tasks = BackgroundTasks()
        queued = verify_news(
            NewsVerifyRequest(
                text="Neutral report text with enough length to satisfy validation and no dramatic claims."
            ),
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


def test_system_status_exposes_demo_configuration() -> None:
    response = get_system_status()

    assert response.supported_modes == ["image", "news", "audio"]
    assert response.upload_storage == "local-filesystem"
    assert response.news_url_fetch_enabled is True
    assert response.datasets
    assert response.sample_sources
    assert response.model_status
    assert response.model_registry
    assert response.benchmark_suite
