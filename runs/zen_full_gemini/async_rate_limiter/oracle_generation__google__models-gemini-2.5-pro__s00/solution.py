import asyncio
import collections
import time
from typing import Callable, Deque, Optional


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows a fixed number of acquisitions
    per one-second window.
    """

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None):
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second. Must be
                  a positive integer.
            now: An optional callable that returns the current time as a float.
                 If None, `time.monotonic` is used, which is suitable for
                 measuring durations.

        Raises:
            ValueError: If `rate` is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")

        self._rate: int = rate
        self._now: Callable[[], float] = now if now is not None else time.monotonic

        self._timestamps: Deque[float] = collections.deque()
        self._lock: asyncio.Lock = asyncio.Lock()

    def _prune_timestamps(self, current_time: float) -> None:
        """
        Removes timestamps from the history that are older than one second.

        This helper must be called within a context where `self._lock` is held.
        """
        one_second_ago = current_time - 1.0
        while self._timestamps and self._timestamps[0] <= one_second_ago:
            self._timestamps.popleft()

    async def acquire(self) -> bool:
        """
        Acquires a permit from the rate limiter, waiting if necessary.

        This coroutine will complete once a permit is available according to the
        configured rate.

        Returns:
            Always returns True upon successful acquisition.
        """
        while True:
            async with self._lock:
                current_time = self._now()
                self._prune_timestamps(current_time)

                if len(self._timestamps) < self._rate:
                    self._timestamps.append(current_time)
                    return True

                # Rate limit is currently exceeded. Calculate the necessary
                # wait time until the oldest timestamp expires.
                oldest_timestamp = self._timestamps[0]
                time_to_wait = (oldest_timestamp + 1.0) - current_time

            # Await the sleep outside the lock to allow other tasks to
            # check the limiter without being blocked by this sleeping task.
            if time_to_wait > 0:
                await asyncio.sleep(time_to_wait)
