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
        # key -> deque of recorded timestamps in ascending order
        self._records: dict[str, deque[int]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_window(self, key: str) -> deque[int]:
        """Return the deque for key, creating it if absent."""
        if key not in self._records:
            self._records[key] = deque()
        return self._records[key]

    def _evict_expired(self, timestamps: deque[int], current: int) -> None:
        """Remove timestamps that fall outside (current - window_seconds, current]."""
        cutoff = current - self._window
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event when the key is within rate limit.
        Return False without recording when the limit is already reached.
        """
        timestamps = self._get_window(key)
        self._evict_expired(timestamps, timestamp)

        if len(timestamps) >= self._limit:
            return False

        timestamps.append(timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        """Return a copy of the retained timestamps for key."""
        if key not in self._records:
            return []
        return list(self._records[key])
