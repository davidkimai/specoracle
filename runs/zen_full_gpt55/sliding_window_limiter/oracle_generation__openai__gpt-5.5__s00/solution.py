from collections import deque
from typing import Deque


def _require_int(name: str, value: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an int")
    return value


def _require_positive_int(name: str, value: int) -> int:
    value = _require_int(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _require_key(key: str) -> str:
    if not isinstance(key, str):
        raise TypeError("key must be a str")
    return key


def _drop_expired(events: Deque[int], cutoff: int) -> None:
    while events and events[0] <= cutoff:
        events.popleft()


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = _require_positive_int("limit", limit)
        self.window_seconds = _require_positive_int("window_seconds", window_seconds)
        self._events: dict[str, Deque[int]] = {}
        self._latest_timestamp: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        key = _require_key(key)
        timestamp = _require_int("timestamp", timestamp)

        latest = self._latest_timestamp.get(key)
        if latest is not None and timestamp < latest:
            raise ValueError("timestamp must be non-decreasing for each key")

        events = self._events.get(key)
        if events is None:
            events = deque()
            self._events[key] = events

        cutoff = timestamp - self.window_seconds
        _drop_expired(events, cutoff)
        self._latest_timestamp[key] = timestamp

        if len(events) >= self.limit:
            return False

        events.append(timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        key = _require_key(key)
        events = self._events.get(key)
        if events is None:
            return []
        return list(events)
