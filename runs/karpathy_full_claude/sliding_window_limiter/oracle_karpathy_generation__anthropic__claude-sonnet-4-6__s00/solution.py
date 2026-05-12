from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self._limit = limit
        self._window = window_seconds
        self._events: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str, timestamp: int) -> bool:
        dq = self._events[key]
        cutoff = timestamp - self._window
        while dq and dq[0] <= cutoff:
            dq.popleft()
        if len(dq) < self._limit:
            dq.append(timestamp)
            return True
        return False

    def snapshot(self, key: str) -> list:
        return list(self._events[key])
