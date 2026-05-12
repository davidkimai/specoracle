import asyncio
import collections
import time
from typing import Callable, Deque

class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows a specified number of successful
    acquisitions within a one-second sliding window.
    """

    def __init__(self, rate: int, *, now: Callable[[], float] | None = None):
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
                  Must be a positive integer.
            now: An optional callable that returns the current time as a float.
                 If None, `time.time` is used. This is primarily for testing.

        Raises:
            ValueError: If rate is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")

        self.rate = rate
        self._now = now if now is not None else time.time

        # A deque to store the timestamps of recent acquisitions.
        # Using maxlen ensures the deque never grows beyond the rate limit,
        # automatically discarding the oldest timestamps as new ones are added.
        self._timestamps: Deque[float] = collections.deque(maxlen=self.rate)

        # A lock to ensure that concurrent calls to acquire() are handled safely.
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquires a permit from the rate limiter, blocking if necessary.

        This method will wait until a permit is available according to the
        rate limit before proceeding.

        Returns:
            True once the permit has been successfully acquired.
        """
        async with self._lock:
            current_time = self._now()

            # If the deque is full, it means we have made `rate` acquisitions
            # in the recent past. We must check if the oldest acquisition is
            # still within the one-second window.
            if len(self._timestamps) == self.rate:
                oldest_timestamp = self._timestamps[0]
                time_since_oldest = current_time - oldest_timestamp

                # If the oldest acquisition was less than a second ago, we need
                # to wait for that one-second window to pass.
                if time_since_oldest < 1.0:
                    wait_time = 1.0 - time_since_oldest
                    await asyncio.sleep(wait_time)
                
                # After waiting, update the current time for the new timestamp.
                current_time = self._now()

            self._timestamps.append(current_time)
            return True
