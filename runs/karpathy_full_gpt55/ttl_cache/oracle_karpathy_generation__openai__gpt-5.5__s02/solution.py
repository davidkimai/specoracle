from collections import OrderedDict
from time import monotonic


class TTLCache:
    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")

        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._now = monotonic if now is None else now
        self._data = OrderedDict()

    def set(self, key, value):
        current_time = self._now()

        if self.max_size == 0:
            self._data.clear()
            return

        self._remove_expired(current_time)

        self._data[key] = (value, current_time + self.ttl_seconds)
        self._data.move_to_end(key)

        while len(self._data) > self.max_size:
            self._data.popitem(last=False)

    def get(self, key):
        current_time = self._now()

        try:
            value, expires_at = self._data[key]
        except KeyError:
            return None

        if expires_at <= current_time:
            del self._data[key]
            return None

        self._data.move_to_end(key)
        return value

    def _remove_expired(self, current_time):
        expired_keys = [
            key for key, (_, expires_at) in self._data.items()
            if expires_at <= current_time
        ]
        for key in expired_keys:
            del self._data[key]
