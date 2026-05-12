from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable
from numbers import Real


class AsyncRateLimiter:
    """An asynchronous, non-blocking sliding-window rate limiter."""

    def __init__(self, rate: int, *, now: Callable[[], Real] | None = None) -> None:
        if not isinstance(rate, int) or isinstance(rate, bool):
            raise TypeError("rate must be an integer")
        if rate <= 0:
            raise ValueError("rate must be positive")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self._rate = rate
        self._now = time.monotonic if now is None else now
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Return True if an acquisition is allowed now; otherwise return False."""
        async with self._lock:
            current_time = self._current_time()
            self._discard_expired(current_time)

            if len(self._timestamps) >= self._rate:
                return False

            self._timestamps.append(current_time)
            return True

    def _current_time(self) -> float:
        value = self._now()
        if not isinstance(value, Real) or isinstance(value, bool):
            raise TypeError("now must return a real number")
        return float(value)

    def _discard_expired(self, current_time: float) -> None:
        cutoff = current_time - 1.0
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()
