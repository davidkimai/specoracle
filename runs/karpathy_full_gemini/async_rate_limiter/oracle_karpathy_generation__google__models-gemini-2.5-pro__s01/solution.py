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

    This implementation uses a sliding window algorithm based on timestamps
    stored in a deque. It is designed to be safe for concurrent use from
    multiple asyncio tasks.
    """

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None):
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per one-second
                  window. Must be a positive integer.
            now: An optional callable that returns the current time as a float.
                 If None, `time.monotonic` is used. This is primarily for
                 deterministic testing.

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
        """
        Acquires a permit from the rate limiter, blocking if necessary.

        This method will wait until a permit becomes available according to the
        configured rate limit. Each successful acquisition is recorded with a
        timestamp.

        Returns:
            True, once the acquisition is successful.
        """
        async with self._lock:
            current_time = self._now()

            # Prune timestamps that are older than the 1-second window.
            # The window is defined as (current_time - 1.0, current_time].
            while self._timestamps and self._timestamps[0] <= current_time - 1.0:
                self._timestamps.popleft()

            # If the number of timestamps in the window has reached the rate limit,
            # we must wait for the oldest timestamp to expire.
            if len(self._timestamps) >= self._rate:
                # The oldest timestamp is at the front of the deque.
                oldest_timestamp = self._timestamps[0]
                # Calculate the time to wait until the oldest timestamp falls
                # out of the 1-second window.
                time_to_wait = (oldest_timestamp + 1.0) - current_time

                if time_to_wait > 0:
                    await asyncio.sleep(time_to_wait)

                # After waiting, update the current time and prune again.
                # This ensures the slot we waited for is now free.
                current_time = self._now()
                while self._timestamps and self._timestamps[0] <= current_time - 1.0:
                    self._timestamps.popleft()

            # A slot is now available; record the acquisition and return.
            self._timestamps.append(current_time)
            return True
