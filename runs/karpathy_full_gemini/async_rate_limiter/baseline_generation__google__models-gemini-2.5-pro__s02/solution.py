"""
An asynchronous rate limiter using a sliding window algorithm.
"""

import asyncio
import collections
import time
from typing import Callable


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows a specified number of acquisitions
    per one-second window.

    This implementation uses a sliding window approach with a deque to store
    timestamps of recent acquisitions. It is safe for concurrent use.
    """

    def __init__(self, rate: int, *, now: Callable[[], float] | None = None):
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
                  Must be a positive integer.
            now: An optional callable that returns the current time as a float.
                 If None, `time.monotonic` is used. This is useful for
                 deterministic testing.

        Raises:
            ValueError: If `rate` is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")

        self._rate = rate
        self._now = now or time.monotonic
        self._timestamps: collections.deque[float] = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquires a permit from the rate limiter, waiting if necessary.

        This method will wait (asynchronously) until a permit becomes
        available according to the specified rate limit.

        Returns:
            Always returns True upon successful acquisition. The boolean return
            type is for API consistency and potential future extensions, such
            as adding a timeout.
        """
        while True:
            async with self._lock:
                current_time = self._now()

                # Remove timestamps that are older than the 1-second window.
                window_start = current_time - 1.0
                while self._timestamps and self._timestamps[0] <= window_start:
                    self._timestamps.popleft()

                # If there's room in the window, acquire a permit and return.
                if len(self._timestamps) < self._rate:
                    self._timestamps.append(current_time)
                    return True

                # If the window is full, calculate the time to wait until the
                # oldest timestamp expires, freeing up a slot.
                oldest_timestamp = self._timestamps[0]
                wait_time = (oldest_timestamp + 1.0) - current_time

            # Wait outside the lock to allow other tasks to run.
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            # Loop again to re-evaluate the state. Another task might have
            # acquired the slot we were waiting for.
