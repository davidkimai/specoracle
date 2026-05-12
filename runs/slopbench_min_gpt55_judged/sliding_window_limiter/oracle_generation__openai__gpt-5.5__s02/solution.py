from collections import deque
from typing import Deque


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer")
        if not isinstance(window_seconds, int) or isinstance(window_seconds, bool):
            raise TypeError("window_seconds must be an integer")
        if limit <= 0:
            raise ValueError("limit must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, Deque[int]] = {}
        self._last_timestamp: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        self._validate_key(key)
        self._validate_timestamp(timestamp)

        last_timestamp = self._last_timestamp.get(key)
        if last_timestamp is not None and timestamp < last_timestamp:
            raise ValueError("timestamp must be non-decreasing for each key")

        self._last_timestamp[key] = timestamp

        events = self._events.setdefault(key, deque())
        self._discard_expired(events, timestamp)

        if len(events) >= self.limit:
            return False

        events.append(timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        self._validate_key(key)
        return list(self._events.get(key, ()))

    def _discard_expired(self, events: Deque[int], timestamp: int) -> None:
        oldest_allowed = timestamp - self.window_seconds
        while events and events[0] <= oldest_allowed:
            events.popleft()

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str):
            raise TypeError("key must be a string")

    @staticmethod
    def _validate_timestamp(timestamp: int) -> None:
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            raise TypeError("timestamp must be an integer")
