"""
async_rate_limiter.py

Provides an AsyncRateLimiter class that allows at most `rate` successful
acquisitions per one-second sliding window.
"""

import asyncio
import time
from collections import deque


class AsyncRateLimiter:
    """
    Asynchronous token-bucket / sliding-window rate limiter.

    Parameters
    ----------
    rate : int
        Maximum number of successful acquisitions allowed per second.
    now : callable | None
        Optional callable that returns the current time as a float (seconds).
        Defaults to ``time.monotonic``.  Useful for deterministic testing.
    """

    def __init__(self, rate: int, *, now=None):
        if rate <= 0:
            raise ValueError(f"rate must be a positive integer, got {rate!r}")
        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._lock = asyncio.Lock()
        # Stores the timestamps of successful acquisitions within the window.
        self._timestamps: deque = deque()

    async def acquire(self) -> bool:
        """
        Attempt to acquire a token.

        Returns
        -------
        bool
            ``True`` if the acquisition was successful (within the rate limit),
            ``False`` otherwise.
        """
        async with self._lock:
            current = self._now()
            window_start = current - 1.0

            # Remove timestamps that have fallen outside the 1-second window.
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current)
                return True

            return False
