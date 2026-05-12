from bisect import bisect_right, insort_right


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = _positive_integer("limit", limit)
        self.window_seconds = _positive_integer("window_seconds", window_seconds)
        self._events_by_key: dict[str, list[int]] = {}
        self._latest_timestamp_by_key: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        key = _string_key(key)
        timestamp = _integer_timestamp(timestamp)

        events = self._events_by_key.setdefault(key, [])
        self._advance_latest_timestamp(key, timestamp)

        lower_bound = timestamp - self.window_seconds
        events_in_window = _count_in_half_open_window(
            events,
            lower_exclusive=lower_bound,
            upper_inclusive=timestamp,
        )

        if events_in_window >= self.limit:
            return False

        insort_right(events, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        key = _string_key(key)

        events = self._events_by_key.get(key)
        if not events:
            return []

        latest_timestamp = self._latest_timestamp_by_key[key]
        lower_bound = latest_timestamp - self.window_seconds
        start = bisect_right(events, lower_bound)
        return list(events[start:])

    def _advance_latest_timestamp(self, key: str, timestamp: int) -> None:
        current = self._latest_timestamp_by_key.get(key)
        if current is None or timestamp > current:
            self._latest_timestamp_by_key[key] = timestamp


def _positive_integer(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _string_key(key: str) -> str:
    if not isinstance(key, str):
        raise TypeError("key must be a string")
    return key


def _integer_timestamp(timestamp: int) -> int:
    if isinstance(timestamp, bool) or not isinstance(timestamp, int):
        raise TypeError("timestamp must be an integer")
    return timestamp


def _count_in_half_open_window(
    events: list[int],
    lower_exclusive: int,
    upper_inclusive: int,
) -> int:
    start = bisect_right(events, lower_exclusive)
    stop = bisect_right(events, upper_inclusive)
    return stop - start
