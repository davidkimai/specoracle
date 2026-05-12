import asyncio
import time
from collections import deque
from collections.abc import Callable
from numbers import Real


class AsyncRateLimiter:
    def __init__(self, rate: int, *, now: Callable[[], Real] | None = None):
        if isinstance(rate, bool) or not isinstance(rate, int):
            raise TypeError("rate must be an integer")
        if rate <= 0:
            raise ValueError("rate must be positive")
        if now is not None and not callable(now):
            raise TypeError("now must be callable or None")

        self._rate = rate
        self._now = time.monotonic if now is None else now
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()
        self._last_seen: float | None = None

    async def acquire(self) -> bool:
        current_time = self._read_time()

        async with self._lock:
            if self._last_seen is not None and current_time < self._last_seen:
                raise ValueError("now must not move backwards")
            self._last_seen = current_time

            self._remove_expired(current_time)

            if len(self._timestamps) >= self._rate:
                return False

            self._timestamps.append(current_time)
            return True

    def _read_time(self) -> float:
        value = self._now()
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError("now must return a real number")
        return float(value)

    def _remove_expired(self, current_time: float) -> None:
        cutoff = current_time - 1.0
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()
