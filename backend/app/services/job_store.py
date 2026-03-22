from __future__ import annotations

import json
import logging
from threading import Lock
from typing import Protocol

import redis

from app.config import get_settings
from app.schemas import StoredJob

logger = logging.getLogger(__name__)
settings = get_settings()

JOB_KEY_PREFIX = "deepguard:job:"
JOB_TTL_SECONDS = 60 * 60 * 6  # 6 hours


class JobStore(Protocol):
    def create(self, job: StoredJob) -> StoredJob: ...

    def update(self, task_id: str, **changes: object) -> StoredJob | None: ...

    def get(self, task_id: str) -> StoredJob | None: ...

    def delete(self, task_id: str) -> None: ...

    def clear(self) -> None: ...


class InMemoryJobStore:
    """Simple in-memory task tracker for local development and unit tests."""

    def __init__(self) -> None:
        self._jobs: dict[str, StoredJob] = {}
        self._lock = Lock()

    def create(self, job: StoredJob) -> StoredJob:
        with self._lock:
            self._jobs[job.task_id] = job
            return job

    def update(self, task_id: str, **changes: object) -> StoredJob | None:
        with self._lock:
            current = self._jobs.get(task_id)
            if current is None:
                return None
            updated = current.model_copy(update=changes)
            self._jobs[task_id] = updated
            return updated

    def get(self, task_id: str) -> StoredJob | None:
        with self._lock:
            return self._jobs.get(task_id)

    def delete(self, task_id: str) -> None:
        with self._lock:
            self._jobs.pop(task_id, None)

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()


class RedisJobStore:
    """Redis-backed job store for multi-process / Celery deployments."""

    def __init__(self, redis_url: str) -> None:
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def _key(self, task_id: str) -> str:
        return f"{JOB_KEY_PREFIX}{task_id}"

    def create(self, job: StoredJob) -> StoredJob:
        key = self._key(job.task_id)
        self._client.set(key, json.dumps(job.model_dump()), ex=JOB_TTL_SECONDS)
        return job

    def update(self, task_id: str, **changes: object) -> StoredJob | None:
        current = self.get(task_id)
        if current is None:
            return None
        updated = current.model_copy(update=changes)
        key = self._key(task_id)
        self._client.set(key, json.dumps(updated.model_dump()), ex=JOB_TTL_SECONDS)
        return updated

    def get(self, task_id: str) -> StoredJob | None:
        raw = self._client.get(self._key(task_id))
        if not raw:
            return None
        return StoredJob.model_validate(json.loads(raw))

    def delete(self, task_id: str) -> None:
        self._client.delete(self._key(task_id))

    def clear(self) -> None:
        # Intended for tests/local; avoid KEYS in production.
        for key in self._client.scan_iter(match=f"{JOB_KEY_PREFIX}*"):
            self._client.delete(key)


def _build_job_store() -> JobStore:
    # If Celery is enabled, we strongly prefer a shared store so the API process
    # can see worker updates. If Redis is unavailable, fall back to in-memory.
    if settings.enable_celery_workers:
        try:
            store = RedisJobStore(settings.redis_url)
            store._client.ping()
            return store
        except Exception as exc:
            logger.warning("Redis job store unavailable; falling back to in-memory store: %s", exc)
            return InMemoryJobStore()
    return InMemoryJobStore()


job_store: JobStore = _build_job_store()
