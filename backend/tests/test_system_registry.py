from __future__ import annotations

from pathlib import Path

from app.api.v1.system import get_system_status
from app.services.benchmark_runner import run_benchmark_suite


def test_system_status_exposes_model_registry_and_benchmark_suite() -> None:
    response = get_system_status()

    assert response.model_registry
    assert any(item.mode == "news" for item in response.model_registry)
    assert response.benchmark_suite
    assert any(item.mode == "news" for item in response.benchmark_suite)


def test_benchmark_suite_runs_required_news_cases() -> None:
    project_root = Path(__file__).resolve().parents[2]
    results = run_benchmark_suite(project_root)

    assert any(item.mode == "news" for item in results)
    assert any(item.status in {"passed", "failed"} for item in results if item.mode == "news")
