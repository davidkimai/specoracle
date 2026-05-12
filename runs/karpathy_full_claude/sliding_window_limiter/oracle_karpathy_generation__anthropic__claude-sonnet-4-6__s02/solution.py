from collections import defaultdict


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self._limit = limit
        self._window = window_seconds
        self._store = defaultdict(list)

    def allow(self, key: str, timestamp: int) -> bool:
        cutoff = timestamp - self._window
        timestamps = self._store[key]
        # Evict timestamps outside the window
        retained = [t for t in timestamps if t > cutoff]
        if len(retained) < self._limit:
            retained.append(timestamp)
            self._store[key] = retained
            return True
        self._store[key] = retained
        return False

    def snapshot(self, key: str) -> list:
        return list(self._store[key])
