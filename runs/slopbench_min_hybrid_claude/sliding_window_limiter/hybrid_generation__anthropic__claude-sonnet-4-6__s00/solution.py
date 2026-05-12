"""
sliding_window_limiter.py

A sliding-window rate limiter keyed by arbitrary strings.
"""

from collections import defaultdict
import bisect


class SlidingWindowLimiter:
    """Rate limiter using a half-open sliding window (timestamp - window_seconds, timestamp]."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit!r}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds!r}")

        self._limit = limit
        self._window = window_seconds
        # Sorted list of timestamps per key.
        self._store: dict[str, list[int]] = defaultdict(list)

    def _drop_expired(self, timestamps: list[int], cutoff: int) -> None:
        """Remove timestamps that fall outside the window in-place."""
        first_valid = bisect.bisect_right(timestamps, cutoff)
        del timestamps[:first_valid]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event when the key is within its rate limit.
        Return False without recording when the limit is already reached.
        """
        timestamps = self._store[key]
        cutoff = timestamp - self._window  # window is (cutoff, timestamp]
        self._drop_expired(timestamps, cutoff)

        if len(timestamps) >= self._limit:
            return False

        bisect.insort(timestamps, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        """Return a copy of the retained timestamps for key."""
        return list(self._store[key])
