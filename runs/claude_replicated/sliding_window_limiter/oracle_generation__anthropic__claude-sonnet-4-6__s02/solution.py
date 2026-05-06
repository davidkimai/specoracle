"""
sliding_window_limiter.py

A sliding-window rate limiter keyed by arbitrary string keys.
"""

from collections import deque


class SlidingWindowLimiter:
    """Rate limiter using a half-open sliding window (timestamp - window_seconds, timestamp]."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit!r}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds!r}")

        self._limit = limit
        self._window = window_seconds
        # key -> deque of accepted timestamps in ascending order
        self._store: dict[str, deque[int]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_expired(self, timestamps: deque[int], current: int) -> None:
        """Remove timestamps that fall outside (current - window_seconds, current]."""
        cutoff = current - self._window
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

    def _timestamps_for(self, key: str) -> deque[int]:
        if key not in self._store:
            self._store[key] = deque()
        return self._store[key]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if the key has fewer than *limit*
        events in (timestamp - window_seconds, timestamp].
        Return False without recording otherwise.
        """
        timestamps = self._timestamps_for(key)
        self._evict_expired(timestamps, timestamp)

        if len(timestamps) < self._limit:
            timestamps.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> list[int]:
        """Return the currently retained timestamps for *key* as a sorted list."""
        if key not in self._store:
            return []
        return list(self._store[key])
