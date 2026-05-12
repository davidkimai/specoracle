from bisect import bisect_right, insort
from typing import Dict, List


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not isinstance(window_seconds, int)
            or isinstance(window_seconds, bool)
            or limit <= 0
            or window_seconds <= 0
        ):
            raise ValueError("limit and window_seconds must be positive integers")

        self.limit = limit
        self.window_seconds = window_seconds
        self._events: Dict[str, List[int]] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        events = self._events.setdefault(key, [])
        cutoff = timestamp - self.window_seconds

        expired_count = bisect_right(events, cutoff)
        if expired_count:
            del events[:expired_count]

        in_window_count = bisect_right(events, timestamp)
        if in_window_count < self.limit:
            insort(events, timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        return list(self._events.get(key, []))
