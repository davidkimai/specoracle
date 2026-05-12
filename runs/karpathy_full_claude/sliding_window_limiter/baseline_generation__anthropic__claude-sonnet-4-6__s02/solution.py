"""
sliding_window_limiter.py

Implements a SlidingWindowLimiter that uses a sliding window algorithm
to rate-limit events per key.
"""

from collections import defaultdict
import bisect


class SlidingWindowLimiter:
    """
    A sliding window rate limiter.

    Parameters
    ----------
    limit : int
        Maximum number of events allowed within the window.
    window_seconds : int
        The size of the sliding window in seconds.
    """

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be a positive integer, got {limit!r}")
        if window_seconds <= 0:
            raise ValueError(
                f"window_seconds must be a positive integer, got {window_seconds!r}"
            )
        self._limit = limit
        self._window = window_seconds
        # Each key maps to a sorted list of timestamps
        self._store: dict[str, list[int]] = defaultdict(list)

    def _evict(self, key: str, timestamp: int) -> None:
        """Remove timestamps that fall outside the half-open window
        (timestamp - window_seconds, timestamp]."""
        cutoff = timestamp - self._window  # strictly less than this is outside
        timestamps = self._store[key]
        # All timestamps <= cutoff are outside the window
        idx = bisect.bisect_right(timestamps, cutoff)
        if idx:
            del timestamps[:idx]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determine whether a new event at *timestamp* for *key* is allowed.

        Returns True and records the event if the number of events in the
        half-open window (timestamp - window_seconds, timestamp] is strictly
        less than the limit. Returns False without recording otherwise.
        """
        self._evict(key, timestamp)
        timestamps = self._store[key]
        if len(timestamps) < self._limit:
            # Insert in sorted order (bisect keeps the list sorted)
            bisect.insort(timestamps, timestamp)
            return True
        return False

    def snapshot(self, key: str) -> list[int]:
        """
        Return a copy of the retained timestamps for *key*.

        Note: this does NOT evict old entries relative to any particular
        timestamp; it returns whatever is currently stored.
        """
        return list(self._store[key])
