from bisect import bisect_right, insort_right


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if type(limit) is not int or type(window_seconds) is not int:
            raise ValueError("limit and window_seconds must be positive")
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")

        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, list[int]] = {}
        self._retained: dict[str, list[int]] = {}
        self._max_seen: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        events = self._events.setdefault(key, [])
        retained = self._retained.setdefault(key, [])

        max_seen = self._max_seen.get(key)
        if max_seen is None or timestamp > max_seen:
            self._max_seen[key] = timestamp
            cutoff = timestamp - self.window_seconds
            expired = bisect_right(retained, cutoff)
            if expired:
                del retained[:expired]

        cutoff = timestamp - self.window_seconds
        start = bisect_right(events, cutoff)
        end = bisect_right(events, timestamp)

        if end - start >= self.limit:
            return False

        insort_right(events, timestamp)

        retention_cutoff = self._max_seen[key] - self.window_seconds
        if timestamp > retention_cutoff:
            insort_right(retained, timestamp)

        return True

    def snapshot(self, key: str) -> list[int]:
        return list(self._retained.get(key, []))
