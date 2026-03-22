from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO

from app.config import get_settings


settings = get_settings()


def _upload_root() -> Path:
    root = Path(settings.upload_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def store_upload(*, request_id: str, request_type: str, file_name: str, content: bytes) -> str:
    """Persist an uploaded file to local storage for async processing."""

    target_dir = _upload_root() / request_type / request_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file_name
    target_path.write_bytes(content)
    return str(target_path)


def store_upload_stream(
    *,
    request_id: str,
    request_type: str,
    file_name: str,
    source: BinaryIO,
    max_bytes: int,
    chunk_size: int = 1024 * 1024,
) -> tuple[str, int]:
    """Stream an uploaded file to local storage without loading it into memory."""

    target_dir = _upload_root() / request_type / request_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file_name

    total = 0
    try:
        with target_path.open("wb") as out:
            while True:
                chunk = source.read(chunk_size)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("upload_too_large")
                out.write(chunk)
    except Exception:
        if target_path.exists():
            target_path.unlink(missing_ok=True)
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        raise

    return str(target_path), total


def load_upload_bytes(file_path: str) -> bytes:
    """Load bytes from a stored upload path."""

    return Path(file_path).read_bytes()


def delete_upload(file_path: str | None) -> None:
    """Delete a stored upload file and its empty parent directory."""

    if not file_path:
        return

    path = Path(file_path)
    if path.exists():
        path.unlink(missing_ok=True)
    parent = path.parent
    if parent.exists():
        shutil.rmtree(parent, ignore_errors=True)
