"""
sliding_window_limiter.py

Implements a sliding window rate limiter.
"""

from collections import defaultdict
import bisect


class SlidingWindowLimiter:
    """Rate limiter using a sliding window algorithm."""

    def __init__(self, limit: int, window_seconds: int):
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")
        self._limit = limit
        self._window_seconds = window_seconds
        # Store sorted list of timestamps per key
        self._timestamps: dict[str, list[int]] = defaultdict(list)

    def _evict(self, key: str, timestamp: int) -> None:
        """Remove timestamps that fall outside the window for the given timestamp."""
        cutoff = timestamp - self._window_seconds  # window is (cutoff, timestamp]
        ts_list = self._timestamps[key]
        # Find the index of the first timestamp > cutoff
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
            # Insert in sorted order
            bisect.insort(ts_list, timestamp)
            return True
        return False

    def remaining(self, key: str, timestamp: int) -> int:
        """
        Prune timestamps outside the window for key at timestamp (same as
        allow()), without recording a new event, and return how many more
        events can still be accepted.
        """
        self._evict(key, timestamp)
        ts_list = self._timestamps[key]
        return max(0, self._limit - len(ts_list))

    def snapshot(self, key: str) -> list[int]:
        """Return a copy of retained timestamps for the given key."""
        return list(self._timestamps.get(key, []))
