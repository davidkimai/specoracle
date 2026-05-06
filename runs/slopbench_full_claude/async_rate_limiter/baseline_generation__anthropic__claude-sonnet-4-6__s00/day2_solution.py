"""
async_rate_limiter.py

Provides an AsyncRateLimiter class that allows at most `rate` successful
acquisitions per one-second sliding window.
"""

import asyncio
import collections
import time


class AsyncRateLimiter:
    """
    Asynchronous token-bucket / sliding-window rate limiter.

    Parameters
    ----------
    rate : int
        Maximum number of successful acquisitions allowed per second.
    now : callable | None
        Optional callable that returns the current time as a float
        (seconds).  Defaults to ``time.monotonic``.  Useful for
        deterministic testing.
    """

    def __init__(self, rate: int, *, now=None):
        if rate <= 0:
            raise ValueError(
                f"rate must be a positive integer, got {rate!r}"
            )
        self._rate = rate
        self._now = now if now is not None else time.monotonic
        # Deque of timestamps for successful acquisitions within the
        # current sliding window.
        self._timestamps: collections.deque = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Attempt to acquire a token.

        Returns
        -------
        bool
            ``True`` if the acquisition succeeded (i.e. the rate limit
            has not been exceeded), ``False`` otherwise.
        """
        async with self._lock:
            current = self._now()
            window_start = current - 1.0

            # Discard timestamps that have fallen outside the 1-second window.
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current)
                return True

            return False

    async def __aenter__(self):
        """
        Enter the async context manager by calling acquire().

        Raises
        ------
        RuntimeError
            If the acquisition is denied (rate limit exceeded).
        """
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError(
                "AsyncRateLimiter: rate limit exceeded, acquisition denied"
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager without additional action."""
        return False
