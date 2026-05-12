from bisect import bisect_right, insort


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if (
            not isinstance(limit, int)
            or not isinstance(window_seconds, int)
            or limit <= 0
            or window_seconds <= 0
        ):
            raise ValueError("limit and window_seconds must be positive integers")

        self.limit = limit
        self.window_seconds = window_seconds
        self._events = {}

    def allow(self, key: str, timestamp: int) -> bool:
        events = self._events.setdefault(key, [])
        cutoff = timestamp - self.window_seconds

        expired = bisect_right(events, cutoff)
        if expired:
            del events[:expired]

        count = bisect_right(events, timestamp)
        if count >= self.limit:
            return False

        insort(events, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        return list(self._events.get(key, []))
