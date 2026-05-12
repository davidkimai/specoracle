"""
sliding_window_limiter.py

Implements a sliding window rate limiter.
"""

from collections import defaultdict
import bisect


class SlidingWindowLimiter:
    """
    A sliding window rate limiter.

    Allows at most `limit` events per `window_seconds` seconds for each key.
    The window is half-open: (timestamp - window_seconds, timestamp].
    """

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")
        self._limit = limit
        self._window = window_seconds
        # Maps key -> sorted list of timestamps
        self._records: dict[str, list[int]] = defaultdict(list)

    def _evict(self, key: str, timestamp: int) -> None:
        """Remove timestamps outside the window (timestamp - window_seconds, timestamp]."""
        cutoff = timestamp - self._window  # timestamps must be > cutoff
        timestamps = self._records[key]
        # Find the index of the first timestamp that is > cutoff
        idx = bisect.bisect_right(timestamps, cutoff)
        if idx > 0:
            self._records[key] = timestamps[idx:]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if fewer than limit events for key
        occurred in the half-open window (timestamp - window_seconds, timestamp].
        Return False without recording otherwise.
        """
        self._evict(key, timestamp)
        timestamps = self._records[key]
        if len(timestamps) < self._limit:
            bisect.insort(timestamps, timestamp)
            return True
        return False

    def snapshot(self, key: str) -> list[int]:
        """Return a copy of the retained timestamps for the given key."""
        return list(self._records.get(key, []))
