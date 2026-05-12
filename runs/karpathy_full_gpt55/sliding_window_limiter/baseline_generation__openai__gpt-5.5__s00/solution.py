from bisect import bisect_right, insort_right


class SlidingWindowLimiter:
    """
    A per-key sliding-window rate limiter.

    Events are counted in the half-open interval
    (timestamp - window_seconds, timestamp].
    """

    __slots__ = ("limit", "window_seconds", "_events", "_latest_timestamp")

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
        self._events: dict[str, list[int]] = {}
        self._latest_timestamp: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        events = self._events.setdefault(key, [])

        latest = self._latest_timestamp.get(key)
        if latest is None or timestamp > latest:
            self._latest_timestamp[key] = timestamp

        cutoff = timestamp - self.window_seconds
        left = bisect_right(events, cutoff)
        right = bisect_right(events, timestamp)

        if right - left >= self.limit:
            return False

        insort_right(events, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        events = self._events.get(key)
        if not events:
            return []

        latest = self._latest_timestamp.get(key)
        if latest is None:
            return []

        cutoff = latest - self.window_seconds
        start = bisect_right(events, cutoff)
        return events[start:]
