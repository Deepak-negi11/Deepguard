from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


WINDOW_SECONDS = 60 * 60


class InMemoryRateLimiter:
    """Simple per-process sliding-window rate limiter."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            events = self._events[key]
            while events and now - events[0] > WINDOW_SECONDS:
                events.popleft()

            if len(events) >= limit:
                retry_after = max(1, int(WINDOW_SECONDS - (now - events[0])))
                return False, retry_after

            events.append(now)
            return True, 0


rate_limiter = InMemoryRateLimiter()
