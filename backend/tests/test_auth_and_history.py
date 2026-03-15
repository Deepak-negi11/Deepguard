import pytest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import ApiUsage
from app.services.job_store import job_store


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> None:
    job_store.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    job_store.clear()
    Base.metadata.drop_all(bind=engine)


def test_register_login_and_history_flow() -> None:
    email = f"tester-{uuid4()}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strongpass123"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "strongpass123"},
    )
    assert login.status_code == 200

    history = client.get("/api/v1/history", headers={"Authorization": f"Bearer {token}"})
    assert history.status_code == 200
    assert history.json()["total"] >= 0


def test_news_verification_returns_rich_analysis_payload() -> None:
    email = f"news-{uuid4()}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strongpass123"},
    )
    token = register.json()["access_token"]

    queued = client.post(
        "/api/v1/verify/news",
        json={
            "url": "https://example.com/story",
            "text": "Breaking exclusive leaked report claims a secret urgent event is unfolding right now.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert queued.status_code == 202
    task_id = queued.json()["task_id"]

    result = client.get(f"/api/v1/results/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert result.status_code == 200
    payload = result.json()["result"]
    assert payload["summary"]
    assert payload["disclaimer"]
    assert payload["recommended_actions"]
    assert payload["input_profile"]["mode"] == "news"
    assert "language_consistency" in payload["breakdown"]
    assert payload["evidence"][0]["details"]


def test_video_verification_rejects_unsupported_file_type() -> None:
    email = f"video-{uuid4()}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strongpass123"},
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/verify/video",
        files={"file": ("payload.txt", b"not-a-video", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 415
    assert "Unsupported video" in response.json()["detail"]


def test_results_endpoint_falls_back_to_persisted_payload_when_job_store_is_empty() -> None:
    email = f"fallback-{uuid4()}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strongpass123"},
    )
    token = register.json()["access_token"]

    queued = client.post(
        "/api/v1/verify/news",
        json={"text": "Neutral report text with enough length to satisfy validation and no dramatic claims."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert queued.status_code == 202
    task_id = queued.json()["task_id"]

    job_store.clear()
    result = client.get(f"/api/v1/results/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert result.status_code == 200
    payload = result.json()
    assert payload["status"] == "completed"
    assert payload["result"]["input_profile"]["mode"] == "news"


def test_api_usage_logging_records_api_requests() -> None:
    email = f"usage-{uuid4()}@example.com"
    before_count = 0
    db = SessionLocal()
    try:
        before_count = db.query(ApiUsage).count()
    finally:
        db.close()

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strongpass123"},
    )
    assert register.status_code == 201

    db = SessionLocal()
    try:
        after_count = db.query(ApiUsage).count()
    finally:
        db.close()
    assert after_count > before_count
