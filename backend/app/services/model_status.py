from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.schemas import ModelStatusEntry

settings = get_settings()
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _BACKEND_ROOT if (_BACKEND_ROOT / "ml_models").exists() else _BACKEND_ROOT.parent

_NEWS_WEIGHTS = _PROJECT_ROOT / "ml_models" / "weights" / "fake_news" / "hamzab-roberta-fake-news-classification"


def _has_model_config(path: Path) -> bool:
    return (path / "config.json").exists()


def build_model_status() -> list[ModelStatusEntry]:
    if settings.enable_demo_analyzers:
        return [
            ModelStatusEntry(
                mode="image",
                analyzer_family="prototype-image-heuristics",
                source="prototype",
                model_id="prototype-image-heuristics",
                local_weights_available=False,
                notes=["Prototype heuristics are active instead of the image classifier."],
            ),
            ModelStatusEntry(
                mode="news",
                analyzer_family="prototype-credibility-heuristics",
                source="prototype",
                model_id="prototype-news-heuristics",
                local_weights_available=False,
                warmup_on_startup=False,
                notes=["Prototype heuristics are active instead of the RoBERTa classifier."],
            ),
        ]

    news_has_local = _has_model_config(_NEWS_WEIGHTS)
    return [
        ModelStatusEntry(
            mode="image",
            analyzer_family="organika/sdxl-detector",
            source="huggingface",
            model_id="Organika/sdxl-detector",
            local_weights_available=False,
            notes=["Image analysis blends C2PA checks, image classification, and forensic artifact signals."],
        ),
        ModelStatusEntry(
            mode="news",
            analyzer_family="roberta-fake-news",
            source="local_weights" if news_has_local else "huggingface",
            model_id="hamzab/roberta-fake-news-classification",
            local_weights_available=news_has_local,
            local_weights_path=str(_NEWS_WEIGHTS) if news_has_local else None,
            warmup_on_startup=settings.warm_news_model_on_startup and settings.enable_celery_workers,
            notes=[
                "Local fine-tuned checkpoint detected."
                if news_has_local
                else "Falls back to the Hugging Face base checkpoint.",
                "Confidence is model confidence, not a proof of authenticity.",
            ],
        ),
    ]
