"""
sliding_window_limiter.py

Implements a SlidingWindowLimiter that uses a sliding window algorithm to
rate-limit events per key.
"""

from collections import defaultdict
from typing import List


class SlidingWindowLimiter:
    """Rate limiter using a sliding window approach.

    For each key, only events whose timestamps fall within the half-open
    interval (timestamp - window_seconds, timestamp] are counted against
    the limit.
    """

    def __init__(self, limit: int, window_seconds: int) -> None:
        """Initialize the limiter.

        Args:
            limit: Maximum number of events allowed within the window.
            window_seconds: Size of the sliding window in seconds.

        Raises:
            ValueError: If limit or window_seconds is not positive.
        """
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds}")

        self._limit = limit
        self._window_seconds = window_seconds
        # Maps key -> sorted list of recorded timestamps
        self._timestamps: dict = defaultdict(list)

    def _evict_old(self, key: str, timestamp: int) -> None:
        """Remove timestamps outside the current window for the given key.

        The window is (timestamp - window_seconds, timestamp], so any
        timestamp <= timestamp - window_seconds is outside the window.
        """
        cutoff = timestamp - self._window_seconds
        ts_list = self._timestamps[key]
        # Find the first index where ts > cutoff
        lo, hi = 0, len(ts_list)
        while lo < hi:
            mid = (lo + hi) // 2
            if ts_list[mid] <= cutoff:
                lo = mid + 1
            else:
                hi = mid
        if lo > 0:
            self._timestamps[key] = ts_list[lo:]

    def allow(self, key: str, timestamp: int) -> bool:
        """Check whether a new event for key at timestamp is allowed.

        Evicts events outside the sliding window first, then checks if the
        number of remaining events is below the limit. If so, records the
        event and returns True. Otherwise returns False without recording.

        Args:
            key: Identifier for the entity being rate-limited.
            timestamp: Integer timestamp of the current event (e.g. Unix seconds).

        Returns:
            True if the event is allowed and has been recorded; False otherwise.
        """
        self._evict_old(key, timestamp)
        ts_list = self._timestamps[key]

        if len(ts_list) < self._limit:
            # Insert timestamp in sorted order (append if monotonically increasing)
            if not ts_list or ts_list[-1] <= timestamp:
                ts_list.append(timestamp)
            else:
                # Binary search for insertion point to maintain sorted order
                lo, hi = 0, len(ts_list)
                while lo < hi:
                    mid = (lo + hi) // 2
                    if ts_list[mid] <= timestamp:
                        lo = mid + 1
                    else:
                        hi = mid
                ts_list.insert(lo, timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        """Return a copy of the retained timestamps for the given key.

        Note: This does NOT evict old entries; it returns whatever is currently
        stored (which may include timestamps from previous windows if allow()
        has not been called recently).

        Args:
            key: Identifier for the entity being queried.

        Returns:
            A list of retained integer timestamps for the key.
        """
        return list(self._timestamps[key])
