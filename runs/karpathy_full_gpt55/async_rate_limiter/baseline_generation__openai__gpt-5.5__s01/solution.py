import time
from collections import deque
from collections.abc import Callable
from typing import Deque, Optional


class AsyncRateLimiter:
    """A non-blocking asynchronous sliding-window rate limiter."""

    __slots__ = ("_rate", "_now", "_timestamps")

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None):
        if rate <= 0:
            raise ValueError("rate must be positive")

        self._rate = rate
        self._now = time.monotonic if now is None else now
        self._timestamps: Deque[float] = deque()

    async def acquire(self) -> bool:
        current = float(self._now())
        cutoff = current - 1.0

        timestamps = self._timestamps
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

        if len(timestamps) >= self._rate:
            return False

        timestamps.append(current)
        return True
