#
# Copyright (c) 2024, The task authors.
# All rights reserved.
#
# Disclaimer: This is a fictional license statement.
#

"""
An asynchronous rate limiter using a sliding window algorithm.
"""

import asyncio
import collections
import time
from typing import Callable, Deque, Optional


class AsyncRateLimiter:
    """Limits the rate of asynchronous operations.

    This class allows a specified number of successful acquisitions per
    one-second sliding window. It is useful for controlling the frequency of
    calls to a service or a resource to avoid overloading it.

    The implementation uses a deque to store timestamps of recent acquisitions
    and an asyncio.Lock to ensure thread-safe and coroutine-safe operations.
    """

    def __init__(
        self, rate: int, *, now: Optional[Callable[[], float]] = None
    ) -> None:
        """Initializes the AsyncRateLimiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
                  Must be a positive integer.
            now: An optional callable that returns the current time in seconds.
                 If None, `time.monotonic` is used. This is primarily for
                 creating deterministic tests.

        Raises:
            ValueError: If `rate` is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")

        self._rate: int = rate
        self._now: Callable[[], float] = now if now is not None else time.monotonic
        self._timestamps: Deque[float] = collections.deque()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquires a permit from the rate limiter.

        If the rate limit has been reached (i.e., the number of acquisitions
        in the last second is equal to the rate), this method will block
        until a permit becomes available.

        Returns:
            Always returns True upon successful acquisition of a permit.
        """
        while True:
            async with self._lock:
                current_time = self._now()

                # Prune timestamps that are older than the 1-second window.
                # The window is defined as (current_time - 1.0, current_time].
                while self._timestamps and self._timestamps[0] <= current_time - 1.0:
                    self._timestamps.popleft()

                if len(self._timestamps) < self._rate:
                    self._timestamps.append(current_time)
                    return True

                # If the window is full, calculate the time to wait until the
                # oldest timestamp expires and a new slot becomes available.
                oldest_timestamp = self._timestamps[0]
                wait_duration = (oldest_timestamp + 1.0) - current_time

            # Sleep outside the lock to allow other tasks to run.
            # This avoids holding the lock while waiting.
            if wait_duration > 0:
                await asyncio.sleep(wait_duration)
