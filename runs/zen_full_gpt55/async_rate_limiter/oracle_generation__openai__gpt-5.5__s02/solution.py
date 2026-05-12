from __future__ import annotations

import asyncio
import math
import time
from collections import deque
from collections.abc import Callable
from numbers import Real

__all__ = ["AsyncRateLimiter"]


def _validate_rate(rate: int) -> int:
    if isinstance(rate, bool) or not isinstance(rate, int):
        raise TypeError("rate must be an integer")
    if rate <= 0:
        raise ValueError("rate must be positive")
    return rate


def _validate_now(now: Callable[[], Real] | None) -> Callable[[], Real]:
    if now is None:
        return time.monotonic
    if not callable(now):
        raise TypeError("now must be callable or None")
    return now


def _validate_time(value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("now() must return a real number")

    current_time = float(value)
    if not math.isfinite(current_time):
        raise ValueError("now() must return a finite number")

    return current_time


class AsyncRateLimiter:
    """Non-blocking asynchronous sliding-window rate limiter."""

    _WINDOW_SECONDS = 1.0

    def __init__(self, rate: int, *, now: Callable[[], Real] | None = None) -> None:
        self._rate = _validate_rate(rate)
        self._now = _validate_now(now)
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()
        self._last_time: float | None = None

    async def acquire(self) -> bool:
        async with self._lock:
            current_time = self._current_time()
            self._discard_expired(current_time)

            if len(self._timestamps) >= self._rate:
                return False

            self._timestamps.append(current_time)
            return True

    def _current_time(self) -> float:
        current_time = _validate_time(self._now())

        if self._last_time is not None and current_time < self._last_time:
            raise ValueError("now() must be monotonic")

        self._last_time = current_time
        return current_time

    def _discard_expired(self, current_time: float) -> None:
        cutoff = current_time - self._WINDOW_SECONDS

        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()
