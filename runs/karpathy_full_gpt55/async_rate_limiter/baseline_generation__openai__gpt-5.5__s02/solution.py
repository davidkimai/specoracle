import asyncio
import time
from collections import deque
from collections.abc import Callable
from typing import Deque, Optional


class AsyncRateLimiter:
    """An asynchronous, non-blocking sliding-window rate limiter."""

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")

        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps: Deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Attempt to acquire one permit.

        Returns True if the acquisition is allowed, otherwise False.
        """
        current = float(self._now())
        cutoff = current - 1.0

        async with self._lock:
            while self._timestamps and self._timestamps[0] <= cutoff:
                self._timestamps.popleft()

            if len(self._timestamps) >= self._rate:
                return False

            self._timestamps.append(current)
            return True
