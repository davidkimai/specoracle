import asyncio
import collections
import time
from typing import Callable, Deque, Optional

__all__ = ["AsyncRateLimiter"]


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that enforces a maximum number of acquisitions
    per a one-second sliding window.
    """

    _rate: int
    _timestamps: Deque[float]
    _lock: asyncio.Lock
    _now: Callable[[], float]

    def __init__(
        self, rate: int, *, now: Optional[Callable[[], float]] = None
    ) -> None:
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
            now: An optional callable that returns the current time as a float.
                 If None, time.monotonic is used. This is useful for testing.

        Raises:
            ValueError: If rate is not a positive integer.
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer.")

        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquires a permit from the rate limiter.

        If the rate limit has been reached for the current window, this method
        will wait until a permit becomes available.

        Returns:
            True upon successful acquisition of a permit.
        """
        while True:
            async with self._lock:
                current_time = self._now()
                boundary = current_time - 1.0

                self._prune_old_timestamps(boundary)

                if len(self._timestamps) < self._rate:
                    self._timestamps.append(current_time)
                    return True

                # The window is full. We must wait.
                # The next available slot opens one second after the oldest
                # timestamp in the current window.
                oldest_timestamp = self._timestamps[0]
                wait_duration = (oldest_timestamp + 1.0) - current_time

            # Wait outside the lock to allow other tasks to proceed.
            if wait_duration > 0:
                await asyncio.sleep(wait_duration)
            # After waiting, loop again to re-acquire the lock and re-evaluate.

    def _prune_old_timestamps(self, boundary: float) -> None:
        """Removes timestamps that are outside the one-second sliding window."""
        while self._timestamps and self._timestamps[0] <= boundary:
            self._timestamps.popleft()
