"""
async_rate_limiter.py

A simple token-bucket-style async rate limiter that allows at most `rate`
successful acquisitions per one-second sliding window.
"""

import asyncio
import time
from collections import deque


class AsyncRateLimiter:
    """Allow at most `rate` acquisitions per one-second window."""

    def __init__(self, rate: int, *, now: callable | None = None):
        if rate <= 0:
            raise ValueError(f"rate must be positive, got {rate!r}")
        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    def _drop_expired(self, current: float) -> None:
        """Remove timestamps outside the one-second window."""
        cutoff = current - 1.0
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    async def acquire(self) -> bool:
        """
        Attempt to acquire a token.

        Returns True if the acquisition is allowed, False if the rate limit
        has been reached for the current one-second window.
        """
        async with self._lock:
            current = self._now()
            self._drop_expired(current)
            if len(self._timestamps) < self._rate:
                self._timestamps.append(current)
                return True
            return False
