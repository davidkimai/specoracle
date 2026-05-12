from bisect import bisect_right, insort_right


class SlidingWindowLimiter:
    """A per-key sliding-window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, int)
            or window_seconds <= 0
        ):
            raise ValueError("window_seconds must be a positive integer")

        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, list[int]] = {}
        self._max_timestamp: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Return True and record the event if fewer than `limit` events for `key`
        occurred in the half-open interval:

            (timestamp - window_seconds, timestamp]

        Otherwise return False without recording the event.
        """
        events = self._events.setdefault(key, [])

        previous_max = self._max_timestamp.get(key)
        if previous_max is None or timestamp > previous_max:
            self._max_timestamp[key] = timestamp

        cutoff = timestamp - self.window_seconds
        left = bisect_right(events, cutoff)
        right = bisect_right(events, timestamp)

        if right - left >= self.limit:
            return False

        insort_right(events, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        """Return the retained timestamps for `key`."""
        events = self._events.get(key)
        if not events:
            return []

        max_timestamp = self._max_timestamp.get(key)
        if max_timestamp is None:
            return []

        cutoff = max_timestamp - self.window_seconds
        left = bisect_right(events, cutoff)
        return events[left:].copy()
