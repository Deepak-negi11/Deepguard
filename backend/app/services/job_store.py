from __future__ import annotations

from threading import Lock

from app.schemas import StoredJob


class JobStore:
    """Simple in-memory task tracker for local development and demos."""

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


job_store = JobStore()
