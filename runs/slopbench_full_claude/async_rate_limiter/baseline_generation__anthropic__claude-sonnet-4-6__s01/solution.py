import asyncio
import time
import collections


class AsyncRateLimiter:
    """
    An asynchronous rate limiter that allows at most `rate` successful
    acquisitions per one-second sliding window.
    """

    def __init__(self, rate: int, *, now=None):
        if rate <= 0:
            raise ValueError(f"rate must be positive, got {rate}")
        self._rate = rate
        self._now = now if now is not None else time.monotonic
        self._timestamps = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Attempt to acquire a slot within the current one-second window.

        Returns True if the acquisition is successful (i.e., the number of
        acquisitions in the last second is below the rate limit), False otherwise.
        """
        async with self._lock:
            current = self._now()
            window_start = current - 1.0

            # Remove timestamps outside the current window
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._rate:
                self._timestamps.append(current)
                return True
            else:
                return False
