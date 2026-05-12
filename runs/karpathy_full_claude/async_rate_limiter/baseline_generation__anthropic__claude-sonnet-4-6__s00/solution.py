"""
async_rate_limiter.py

Provides an AsyncRateLimiter class that limits async acquisitions to a given
rate per one-second sliding window.
"""

import asyncio
import collections
import time
from typing import Callable, Optional


class AsyncRateLimiter:
    """
    Allows at most `rate` successful acquisitions per one-second window.

    Parameters
    ----------
    rate : int
        Maximum number of acquisitions allowed per second. Must be positive.
    now : callable, optional
        A callable returning the current time as a float (seconds). Defaults
        to ``time.monotonic``. Useful for deterministic testing.
    """

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None) -> None:
        if rate <= 0:
            raise ValueError(f"rate must be a positive integer, got {rate!r}")
        self._rate = rate
        self._now: Callable[[], float] = now if now is not None else time.monotonic
        # Deque storing timestamps of successful acquisitions within the window
        self._timestamps: collections.deque = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Attempt to acquire a slot.

        Returns
        -------
        bool
            ``True`` if the acquisition was successful (within rate limit),
            ``False`` if the rate limit has been exceeded for the current window.
        """
        async with self._lock:
            current_time = self._now()
            window_start = current_time - 1.0

            # Evict timestamps that are outside the one-second sliding window
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current_time)
                return True

            return False
