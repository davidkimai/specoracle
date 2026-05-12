from bisect import bisect_right, insort_right


class SlidingWindowLimiter:
    __slots__ = ("limit", "window_seconds", "_events", "_retained", "_watermark")

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
        self._events = {}
        self._retained = {}
        self._watermark = {}

    @staticmethod
    def _discard_expired(timestamps: list[int], cutoff: int) -> None:
        index = bisect_right(timestamps, cutoff)
        if index:
            del timestamps[:index]

    def allow(self, key: str, timestamp: int) -> bool:
        events = self._events.get(key)
        if events is None:
            events = []
            self._events[key] = events

        watermark = self._watermark.get(key)
        retained = self._retained.get(key)

        if watermark is None or timestamp > watermark:
            watermark = timestamp
            self._watermark[key] = watermark
            if retained is not None:
                self._discard_expired(retained, watermark - self.window_seconds)

        lower_bound = timestamp - self.window_seconds
        window_start = bisect_right(events, lower_bound)
        window_end = bisect_right(events, timestamp)

        if window_end - window_start >= self.limit:
            return False

        insort_right(events, timestamp)

        cutoff = watermark - self.window_seconds
        if timestamp > cutoff:
            if retained is None:
                retained = []
                self._retained[key] = retained
            insort_right(retained, timestamp)

        return True

    def snapshot(self, key: str) -> list[int]:
        timestamps = self._retained.get(key)
        if timestamps is None:
            return []
        return list(timestamps)
