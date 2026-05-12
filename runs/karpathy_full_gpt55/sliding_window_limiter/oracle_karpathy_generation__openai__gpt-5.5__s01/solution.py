from bisect import bisect_right, insort_right


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, list[int]] = {}
        self._latest: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        latest = self._latest.get(key)
        if latest is None or timestamp > latest:
            self._latest[key] = timestamp

        events = self._events.setdefault(key, [])
        lower = timestamp - self.window_seconds
        start = bisect_right(events, lower)
        end = bisect_right(events, timestamp)

        if end - start >= self.limit:
            return False

        insort_right(events, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        events = self._events.get(key)
        if not events:
            return []

        lower = self._latest[key] - self.window_seconds
        start = bisect_right(events, lower)
        return events[start:]
