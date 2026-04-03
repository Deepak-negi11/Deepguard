from __future__ import annotations

import json
from pathlib import Path


_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _BACKEND_ROOT if (_BACKEND_ROOT / "docs").exists() else _BACKEND_ROOT.parent
_DOCS_ROOT = _PROJECT_ROOT / "docs"


def _load_json_list(file_name: str) -> list[dict]:
    path = _DOCS_ROOT / file_name
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def load_dataset_registry() -> list[dict]:
    return _load_json_list("dataset-registry.json")


def load_model_registry() -> list[dict]:
    return _load_json_list("model-registry.json")


def load_benchmark_suite() -> list[dict]:
    return _load_json_list("benchmark-suite.json")
