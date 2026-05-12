from bisect import bisect_right, insort_right
from typing import Dict, List

__all__ = ["SlidingWindowLimiter"]


class SlidingWindowLimiter:
    """Per-key sliding-window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        if type(limit) is not int or type(window_seconds) is not int:
            raise ValueError("limit and window_seconds must be positive integers")
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive integers")

        self.limit = limit
        self.window_seconds = window_seconds
        self._timestamps: Dict[str, List[int]] = {}
        self._latest_timestamp: Dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        timestamps = self._timestamps.setdefault(key, [])

        window_start = timestamp - self.window_seconds
        left = bisect_right(timestamps, window_start)
        right = bisect_right(timestamps, timestamp)
        count = right - left

        previous_latest = self._latest_timestamp.get(key)
        if previous_latest is None or timestamp > previous_latest:
            self._latest_timestamp[key] = timestamp

        if count >= self.limit:
            return False

        insort_right(timestamps, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        timestamps = self._timestamps.get(key)
        if not timestamps:
            return []

        latest = self._latest_timestamp.get(key)
        if latest is None:
            return []

        retained_after = latest - self.window_seconds
        first_retained = bisect_right(timestamps, retained_after)
        return list(timestamps[first_retained:])
