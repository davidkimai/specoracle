import asyncio
import time
from collections import deque


class AsyncRateLimiter:
    """Async rate limiter allowing at most `rate` acquisitions per second."""

    def __init__(self, rate: int, *, now: callable = None):
        if rate <= 0:
            raise ValueError(f"Rate must be positive, got {rate}")
        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self._lock:
            current = self._now()
            window_start = current - 1.0

            # Remove timestamps outside the current 1-second window
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current)
                return True
            return False

    async def __aenter__(self):
        if not await self.acquire():
            raise RuntimeError("Rate limit exceeded")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False
