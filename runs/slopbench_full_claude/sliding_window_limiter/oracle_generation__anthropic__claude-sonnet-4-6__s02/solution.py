from collections import defaultdict, deque


class SlidingWindowLimiter:
    """Rate limiter using a sliding window of fixed duration."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds}")
        self._limit = limit
        self._window = window_seconds
        self._timestamps: dict[str, deque[int]] = defaultdict(deque)

    def _evict_expired(self, key: str, timestamp: int) -> None:
        """Remove timestamps outside the half-open window (timestamp - window, timestamp]."""
        cutoff = timestamp - self._window
        queue = self._timestamps[key]
        while queue and queue[0] <= cutoff:
            queue.popleft()

    def allow(self, key: str, timestamp: int) -> bool:
        """Return True and record the event if under the rate limit, else False."""
        self._evict_expired(key, timestamp)
        queue = self._timestamps[key]
        if len(queue) < self._limit:
            queue.append(timestamp)
            return True
        return False

    def snapshot(self, key: str) -> list[int]:
        """Return a list of retained timestamps for the given key."""
        return list(self._timestamps[key])
