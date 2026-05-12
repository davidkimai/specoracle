"""
An asynchronous rate limiter.
"""

import asyncio
import collections
import time
from typing import Callable, Deque, Optional

__all__ = ["AsyncRateLimiter"]


def _get_monotonic_time() -> float:
    """Returns the current value of the monotonic clock."""
    return time.monotonic()


def _validate_rate(rate: int) -> None:
    """Raises ValueError if the rate is not a positive integer."""
    if not isinstance(rate, int) or rate <= 0:
        raise ValueError("Rate must be a positive integer.")


def _prune_timestamps(
    timestamps: Deque[float], current_time: float, window_size: float
) -> None:
    """Removes timestamps that are outside the time window."""
    window_start = current_time - window_size
    while timestamps and timestamps[0] <= window_start:
        timestamps.popleft()


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows a certain number of acquisitions
    per one-second window.

    This implementation uses a sliding window algorithm based on a deque of
    timestamps to track recent acquisitions. It is safe for concurrent use
    by multiple asyncio tasks.
    """

    _WINDOW_SIZE: float = 1.0

    def __init__(self, rate: int, *, now: Optional[Callable[[], float]] = None):
        """
        Initializes the rate limiter.

        Args:
            rate: The maximum number of acquisitions allowed per second.
            now: An optional callable that returns the current time as a float.
                 If not provided, `time.monotonic` is used. This is useful for
                 deterministic testing.

        Raises:
            ValueError: If `rate` is not a positive integer.
        """
        _validate_rate(rate)

        self._rate: int = rate
        self._now: Callable[[], float] = now if now is not None else _get_monotonic_time
        self._timestamps: Deque[float] = collections.deque()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquires a token from the limiter, waiting if necessary.

        This method will suspend execution until a token is available according
        to the configured rate limit.

        Returns:
            Always returns `True` upon successful acquisition.
        """
        while True:
            async with self._lock:
                current_time = self._now()
                _prune_timestamps(self._timestamps, current_time, self._WINDOW_SIZE)

                if len(self._timestamps) < self._rate:
                    self._timestamps.append(current_time)
                    return True

                # At capacity, calculate time until the oldest token expires.
                oldest_timestamp = self._timestamps[0]
                wait_time = (oldest_timestamp + self._WINDOW_SIZE) - current_time

            # Sleep outside the lock to allow other tasks to make progress.
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            else:
                # Yield control to the event loop for an immediate retry.
                await asyncio.sleep(0)
