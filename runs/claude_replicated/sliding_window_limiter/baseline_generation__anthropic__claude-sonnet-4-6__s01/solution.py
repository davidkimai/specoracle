from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must both be positive integers")
        self._limit = limit
        self._window_seconds = window_seconds
        self._store: dict[str, deque[int]] = defaultdict(deque)

    def _evict(self, key: str, timestamp: int) -> None:
        dq = self._store[key]
        cutoff = timestamp - self._window_seconds
        while dq and dq[0] <= cutoff:
            dq.popleft()

    def allow(self, key: str, timestamp: int) -> bool:
        self._evict(key, timestamp)
        dq = self._store[key]
        if len(dq) < self._limit:
            dq.append(timestamp)
            return True
        return False

    def snapshot(self, key: str) -> list[int]:
        return list(self._store[key])
