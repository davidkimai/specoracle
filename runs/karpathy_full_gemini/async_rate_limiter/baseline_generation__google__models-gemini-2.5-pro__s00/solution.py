# -*- coding: utf-8 -*-
"""
An asynchronous rate limiter using a sliding window algorithm.
"""

import asyncio
import collections
import time
from typing import Callable, Deque, Optional

__all__ = ["AsyncRateLimiter"]


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows a certain number of acquisitions
    per one-second sliding window.
    """

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None):
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
            now: An optional callable that returns the current time as a float.
                 If None, `time.monotonic` is used. This is useful for
                 deterministic testing.

        Raises:
            ValueError: If the rate is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")

        self.rate: int = rate
        self._now: Callable[[], float] = now if now is not None else time.monotonic
        self._timestamps: Deque[float] = collections.deque()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Attempts to acquire a permit from the rate limiter.

        This method is a coroutine. It ensures that the number of successful
        acquisitions within any one-second window does not exceed the configured
        rate.

        Returns:
            True if the acquisition was successful (i.e., the call is within
            the configured rate limit), False otherwise.
        """
        async with self._lock:
            current_time = self._now()
            
            # Prune timestamps that are older than the 1-second window.
            # The window is (current_time - 1, current_time].
            while self._timestamps and current_time - self._timestamps[0] > 1.0:
                self._timestamps.popleft()

            # Check if the number of recent acquisitions is below the rate limit.
            if len(self._timestamps) < self.rate:
                self._timestamps.append(current_time)
                return True
            else:
                return False
