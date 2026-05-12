"""
sliding_window_limiter.py

Implements a sliding window rate limiter.
"""

from collections import defaultdict
import bisect


class SlidingWindowLimiter:
    """Rate limiter using a sliding window algorithm."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")
        self._limit = limit
        self._window_seconds = window_seconds
        # Store sorted list of timestamps per key
        self._timestamps: dict[str, list[int]] = defaultdict(list)

    def _evict(self, key: str, timestamp: int) -> None:
        """Remove timestamps outside the window (timestamp - window_seconds, timestamp]."""
        cutoff = timestamp - self._window_seconds
        ts_list = self._timestamps[key]
        # Find the first index where ts_list[i] > cutoff
        idx = bisect.bisect_right(ts_list, cutoff)
        if idx > 0:
            self._timestamps[key] = ts_list[idx:]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if fewer than limit events occurred
        in the half-open window (timestamp - window_seconds, timestamp].
        Return False without recording otherwise.
        """
        self._evict(key, timestamp)
        ts_list = self._timestamps[key]
        if len(ts_list) < self._limit:
            bisect.insort(ts_list, timestamp)
            return True
        return False

    def snapshot(self, key: str) -> list[int]:
        """Return the retained timestamps for the given key."""
        return list(self._timestamps[key])
