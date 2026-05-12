from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable


class AsyncRateLimiter:
    """
    Asynchronous, non-blocking sliding-window rate limiter.

    acquire() returns True when the call is permitted and False when the limit
    has already been reached for the preceding one-second window.
    """

    __slots__ = ("_rate", "_now", "_lock", "_timestamps")

    def __init__(self, rate: int, *, now: Callable[[], float] | None = None):
        if not isinstance(rate, int):
            raise TypeError("rate must be an int")
        if rate <= 0:
            raise ValueError("rate must be positive")

        self._rate = rate
        self._now = time.monotonic if now is None else now
        self._lock = asyncio.Lock()
        self._timestamps: deque[float] = deque()

    async def acquire(self) -> bool:
        current = float(self._now())
        cutoff = current - 1.0

        async with self._lock:
            timestamps = self._timestamps

            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= self._rate:
                return False

            timestamps.append(current)
            return True
