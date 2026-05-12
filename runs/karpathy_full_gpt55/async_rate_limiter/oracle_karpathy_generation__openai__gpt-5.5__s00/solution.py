from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable


class AsyncRateLimiter:
    def __init__(self, rate: int, *, now: Callable[[], float] | None = None):
        if rate <= 0:
            raise ValueError("rate must be positive")

        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self._lock:
            current = self._now()
            cutoff = current - 1.0

            while self._timestamps and self._timestamps[0] <= cutoff:
                self._timestamps.popleft()

            if len(self._timestamps) >= self._rate:
                return False

            self._timestamps.append(current)
            return True
