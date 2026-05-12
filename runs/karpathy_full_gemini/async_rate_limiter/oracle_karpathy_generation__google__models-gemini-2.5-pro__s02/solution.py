# SPDX-FileCopyrightText: 2024-present
#
# SPDX-License-Identifier: MIT
"""
An asynchronous rate limiter using a sliding window algorithm.
"""

import asyncio
import collections
import time
from typing import Callable, Deque, Optional


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows a specified number of acquisitions
    per one-second window.
    """

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None) -> None:
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
            now: An optional callable that returns the current time as a float.
                 If None, `time.monotonic` is used. This is primarily for
                 deterministic testing.

        Raises:
            ValueError: If `rate` is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")

        self.rate = rate
        self._now: Callable[[], float] = now or time.monotonic
        self._timestamps: Deque[float] = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquires a permit from the rate limiter.

        If the rate limit has been reached, this method will wait (asynchronously)
        until a permit becomes available.

        Returns:
            True when the permit has been successfully acquired.
        """
        while True:
            async with self._lock:
                current_time = self._now()
                window_start = current_time - 1.0

                # Remove timestamps that are older than the 1-second window.
                while self._timestamps and self._timestamps[0] <= window_start:
                    self._timestamps.popleft()

                # If there's capacity, acquire a permit and return.
                if len(self._timestamps) < self.rate:
                    self._timestamps.append(current_time)
                    return True

                # If at capacity, calculate the time to wait until the oldest
                # permit expires.
                oldest_timestamp = self._timestamps[0]
                sleep_duration = (oldest_timestamp + 1.0) - current_time

            # Wait outside the lock to allow other tasks to run.
            # A small positive sleep_duration is expected. If it's zero or
            # negative due to timing, asyncio.sleep will yield to the event
            # loop and we'll retry immediately, which is correct.
            await asyncio.sleep(sleep_duration)
