"""
sliding_window_limiter.py

A sliding-window rate limiter keyed by arbitrary string keys.
"""

from collections import defaultdict
import bisect


class SlidingWindowLimiter:
    """Rate limiter using a sliding window of fixed duration."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit!r}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds!r}")

        self._limit = limit
        self._window = window_seconds
        # Sorted list of timestamps per key.
        self._store: dict[str, list[int]] = defaultdict(list)

    def _evict_expired(self, key: str, timestamp: int) -> None:
        """Remove timestamps that fall outside the half-open window."""
        timestamps = self._store[key]
        cutoff = timestamp - self._window
        # Keep only timestamps > cutoff (i.e., strictly inside the window).
        first_valid = bisect.bisect_right(timestamps, cutoff)
        if first_valid:
            self._store[key] = timestamps[first_valid:]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if the key has fewer than limit
        events in (timestamp - window_seconds, timestamp].
        Return False without recording otherwise.
        """
        self._evict_expired(key, timestamp)
        timestamps = self._store[key]

        if len(timestamps) >= self._limit:
            return False

        bisect.insort(timestamps, timestamp)
        return True

    def remaining(self, key: str, timestamp: int) -> int:
        """
        Prune expired events the same way allow() does, without recording a
        new event, and return how many more events can still be accepted for
        key at that timestamp.
        """
        self._evict_expired(key, timestamp)
        return max(0, self._limit - len(self._store[key]))

    def snapshot(self, key: str) -> list[int]:
        """Return the currently retained timestamps for key (sorted)."""
        return list(self._store[key])
