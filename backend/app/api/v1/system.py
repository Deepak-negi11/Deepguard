from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import DemoDatasetEntry, DemoSourceLink, SystemStatusResponse
from app.services.news_ingestion import load_dataset_registry

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
    DemoSourceLink(
        label="ASVspoof 2019",
        category="audio",
        url="https://datashare.ed.ac.uk/handle/10283/3336",
        purpose="Official spoofed and bona fide speech dataset for audio demo inputs.",
    ),
    DemoSourceLink(
        label="ElevenLabs voice tools",
        category="audio",
        url="https://elevenlabs.io/docs/product/voices/default-voices",
        purpose="Reference for generating clearly synthetic voice examples for classroom demos.",
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
    )
