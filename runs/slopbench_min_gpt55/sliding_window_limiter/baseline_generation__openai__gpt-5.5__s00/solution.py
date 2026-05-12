from collections import deque
from typing import Deque, Dict, List


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self._limit = limit
        self._window_seconds = window_seconds
        self._events: Dict[str, Deque[int]] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        events = self._events.setdefault(key, deque())
        cutoff = timestamp - self._window_seconds

        while events and events[0] <= cutoff:
            events.popleft()

        if len(events) < self._limit:
            events.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        return list(self._events.get(key, ()))
