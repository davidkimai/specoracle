"""
Sliding window rate limiter.

Tracks per-key event timestamps within a rolling time window and enforces
a configurable request limit over that window.
"""

from collections import defaultdict


class SlidingWindowLimiter:
    """Rate limiter using a sliding window of fixed duration."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit!r}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds!r}")

        self._limit = limit
        self._window = window_seconds
        # key -> list of timestamps in ascending order
        self._records: dict[str, list[int]] = defaultdict(list)

    def _window_start(self, timestamp: int) -> int:
        """Exclusive lower bound of the half-open window (start, timestamp]."""
        return timestamp - self._window

    def _evict_stale(self, key: str, timestamp: int) -> None:
        """Remove timestamps that fall outside the current window."""
        cutoff = self._window_start(timestamp)
        timestamps = self._records[key]
        # Discard entries older than or equal to cutoff (window is half-open)
        keep_from = 0
        for i, ts in enumerate(timestamps):
            if ts > cutoff:
                keep_from = i
                break
        else:
            # All entries are stale if the loop completed without breaking
            keep_from = len(timestamps)
            self._records[key] = []
            return

        self._records[key] = timestamps[keep_from:]

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if the key is under the rate limit.

        The window is half-open: (timestamp - window_seconds, timestamp].
        Returns False without recording if the limit is already reached.
        """
        self._evict_stale(key, timestamp)
        timestamps = self._records[key]

        if len(timestamps) >= self._limit:
            return False

        timestamps.append(timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        """Return a copy of retained timestamps for the given key."""
        return list(self._records[key])
