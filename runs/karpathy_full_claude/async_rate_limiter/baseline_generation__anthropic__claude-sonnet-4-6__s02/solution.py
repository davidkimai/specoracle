"""
async_rate_limiter.py

Provides an AsyncRateLimiter class that limits the number of successful
acquisitions to at most `rate` per one-second sliding window.
"""

import asyncio
import collections
import time
from typing import Callable, Optional


class AsyncRateLimiter:
    """
    An asynchronous token-bucket / sliding-window rate limiter.

    Parameters
    ----------
    rate : int
        Maximum number of successful acquisitions allowed per second.
    now : callable, optional
        A zero-argument callable that returns the current time as a float
        (seconds).  Defaults to ``time.monotonic``.  Useful for
        deterministic testing.

    Raises
    ------
    ValueError
        If *rate* is not a positive integer.
    """

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None) -> None:
        if rate <= 0:
            raise ValueError(f"rate must be a positive integer, got {rate!r}")
        self._rate: int = rate
        self._now: Callable[[], float] = now if now is not None else time.monotonic
        # Deque stores timestamps of successful acquisitions within the current window.
        self._timestamps: collections.deque = collections.deque()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Attempt to acquire a token.

        Returns
        -------
        bool
            ``True`` if the acquisition was successful (i.e. the caller is
            within the allowed rate), ``False`` otherwise.
        """
        async with self._lock:
            current_time = self._now()
            window_start = current_time - 1.0

            # Evict timestamps that are outside the sliding one-second window.
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current_time)
                return True

            return False
