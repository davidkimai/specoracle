"""
Sliding window rate limiter.

Each key maintains a list of timestamps within the current window.
Old timestamps are evicted on every allow() call.
"""

from collections import defaultdict


class SlidingWindowLimiter:
    """Rate limiter using a sliding window of fixed duration."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds}")

        self._limit = limit
        self._window = window_seconds
        self._store: dict[str, list[int]] = defaultdict(list)

    def _evict(self, key: str, timestamp: int) -> None:
        """Remove timestamps that fall outside the half-open window (timestamp - window, timestamp]."""
        cutoff = timestamp - self._window
        self._store[key] = [t for t in self._store[key] if t > cutoff]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if the key has fewer than limit
        events in the window (timestamp - window_seconds, timestamp].
        Return False without recording otherwise.
        """
        self._evict(key, timestamp)

        if len(self._store[key]) < self._limit:
            self._store[key].append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> list[int]:
        """Return the retained timestamps for the given key."""
        return list(self._store[key])
