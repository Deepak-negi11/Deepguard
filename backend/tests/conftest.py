from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT if (BACKEND_ROOT / "ml_models").exists() else BACKEND_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import app.models  # noqa: F401, E402
from app.api.v1.verify import settings as verify_settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.services.job_store import job_store  # noqa: E402


@pytest.fixture(autouse=True)
def reset_test_database() -> None:
    job_store.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    job_store.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def disable_celery_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(verify_settings, "enable_celery_workers", False)
