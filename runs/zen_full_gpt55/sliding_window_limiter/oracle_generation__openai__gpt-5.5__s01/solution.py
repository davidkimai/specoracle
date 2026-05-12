from bisect import bisect_right, insort_right


def _require_int(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    return value


def _require_positive_int(name: str, value: int) -> int:
    value = _require_int(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _require_key(key: str) -> str:
    if not isinstance(key, str):
        raise TypeError("key must be a str")
    return key


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = _require_positive_int("limit", limit)
        self.window_seconds = _require_positive_int(
            "window_seconds",
            window_seconds,
        )
        self._timestamps_by_key: dict[str, list[int]] = {}
        self._latest_timestamp_by_key: dict[str, int] = {}

    def allow(self, key: str, timestamp: int) -> bool:
        key = _require_key(key)
        timestamp = _require_int("timestamp", timestamp)

        timestamps = self._timestamps_by_key.setdefault(key, [])
        cutoff = timestamp - self.window_seconds

        start = bisect_right(timestamps, cutoff)
        end = bisect_right(timestamps, timestamp)
        event_count = end - start

        previous_latest = self._latest_timestamp_by_key.get(key)
        if previous_latest is None or timestamp > previous_latest:
            self._latest_timestamp_by_key[key] = timestamp

        if event_count >= self.limit:
            return False

        insort_right(timestamps, timestamp)
        return True

    def snapshot(self, key: str) -> list[int]:
        key = _require_key(key)

        latest_timestamp = self._latest_timestamp_by_key.get(key)
        if latest_timestamp is None:
            return []

        timestamps = self._timestamps_by_key.get(key, [])
        cutoff = latest_timestamp - self.window_seconds
        start = bisect_right(timestamps, cutoff)
        end = bisect_right(timestamps, latest_timestamp)

        return list(timestamps[start:end])
