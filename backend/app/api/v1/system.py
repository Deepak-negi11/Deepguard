from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import BenchmarkCaseEntry, DemoDatasetEntry, DemoSourceLink, ModelRegistryEntry, SystemStatusResponse
from app.services.model_status import build_model_status
from app.services.system_registry import load_benchmark_suite, load_dataset_registry, load_model_registry

router = APIRouter()
settings = get_settings()

SUPPORTED_MODES = ["image", "news", "audio"]

SAMPLE_SOURCES = [
    DemoSourceLink(
        label="LIAR dataset",
        category="news",
        url="https://www.cs.ucsb.edu/~william/data/liar_dataset.zip",
        purpose="Small labeled fake-news style dataset for text-only demo cases.",
    ),
    DemoSourceLink(
        label="FakeNewsNet",
        category="news",
        url="https://github.com/KaiDMML/FakeNewsNet",
        purpose="Official GitHub dataset tooling for real and fake news examples.",
    ),
    DemoSourceLink(
        label="FaceForensics++",
        category="image",
        url="https://github.com/ondyari/FaceForensics",
        purpose="Official manipulated-face dataset. Use frames if you need still-image samples.",
    ),
]


@router.get("/status", response_model=SystemStatusResponse)
def get_system_status() -> SystemStatusResponse:
    datasets = [
        DemoDatasetEntry(
            key=item.get("key", ""),
            display_name=item.get("display_name", ""),
            category=item.get("category", ""),
            source_url=item.get("source_url", ""),
            access=item.get("access", ""),
            notes=item.get("notes", []),
        )
        for item in load_dataset_registry()
    ]
    model_registry = [
        ModelRegistryEntry(
            key=item.get("key", ""),
            mode=item.get("mode", "news"),
            display_name=item.get("display_name", ""),
            provider=item.get("provider", ""),
            model_id=item.get("model_id", ""),
            source=item.get("source", "huggingface"),
            active_version=item.get("active_version", ""),
            weights_path=item.get("weights_path"),
            dataset_version=item.get("dataset_version"),
            trained_at=item.get("trained_at"),
            validation_accuracy=item.get("validation_accuracy"),
            notes=item.get("notes", []),
        )
        for item in load_model_registry()
    ]
    benchmark_suite = [
        BenchmarkCaseEntry(
            key=item.get("key", ""),
            mode=item.get("mode", "news"),
            title=item.get("title", ""),
            input_kind=item.get("input_kind", "text"),
            expected_verdict=item.get("expected_verdict", "uncertain"),
            text=item.get("text"),
            url=item.get("url"),
            sample_path=item.get("sample_path"),
            required=item.get("required", True),
            notes=item.get("notes", []),
        )
        for item in load_benchmark_suite()
    ]

    return SystemStatusResponse(
        app_name=settings.app_name,
        environment=settings.environment,
        supported_modes=SUPPORTED_MODES,
        demo_analyzers_enabled=settings.enable_demo_analyzers,
        celery_workers_enabled=settings.enable_celery_workers,
        upload_storage="local-filesystem",
        news_url_fetch_enabled=True,
        datasets=datasets,
        sample_sources=SAMPLE_SOURCES,
        model_registry=model_registry,
        model_status=build_model_status(),
        benchmark_suite=benchmark_suite,
    )
