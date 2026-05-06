"""
async_rate_limiter.py

A simple token-bucket-style async rate limiter that allows at most `rate`
acquisitions per one-second sliding window.
"""

import asyncio
import collections
import time


class AsyncRateLimiter:
    """Allow at most `rate` successful acquisitions per one-second window."""

    def __init__(self, rate: int, *, now=None):
        if rate <= 0:
            raise ValueError(f"rate must be a positive integer, got {rate!r}")
        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self._lock:
            current = self._now()
            window_start = current - 1.0

            # Drop timestamps outside the current one-second window.
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current)
                return True

            return False

    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError("AsyncRateLimiter: rate limit exceeded, acquisition denied")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False
