"""
sliding_window_limiter.py

A sliding-window rate limiter keyed by arbitrary string identifiers.
"""

from collections import deque


class SlidingWindowLimiter:
    """Rate limiter using a per-key sliding window of fixed duration."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit!r}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds!r}")

        self._limit = limit
        self._window = window_seconds
        # key -> deque of recorded timestamps (oldest first)
        self._store: dict[str, deque[int]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_expired(self, timestamps: deque[int], cutoff: int) -> None:
        """Remove timestamps that fall outside the half-open window (cutoff, ...]."""
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

    def _window_for(self, key: str) -> deque[int]:
        """Return (and lazily create) the timestamp deque for *key*."""
        if key not in self._store:
            self._store[key] = deque()
        return self._store[key]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record *timestamp* when the key has fewer than
        *limit* events in (timestamp - window_seconds, timestamp].
        Return False without recording when the limit is already reached.
        """
        timestamps = self._window_for(key)
        cutoff = timestamp - self._window
        self._evict_expired(timestamps, cutoff)

        if len(timestamps) >= self._limit:
            return False

        timestamps.append(timestamp)
        return True

    def remaining(self, key: str, timestamp: int) -> int:
        """
        Prune expired events (same window logic as allow()) without recording
        a new event, then return how many more events can still be accepted
        for *key* at *timestamp*.
        """
        timestamps = self._window_for(key)
        cutoff = timestamp - self._window
        self._evict_expired(timestamps, cutoff)
        return max(0, self._limit - len(timestamps))

    def snapshot(self, key: str) -> list[int]:
        """Return a copy of the currently retained timestamps for *key*."""
        if key not in self._store:
            return []
        return list(self._store[key])
