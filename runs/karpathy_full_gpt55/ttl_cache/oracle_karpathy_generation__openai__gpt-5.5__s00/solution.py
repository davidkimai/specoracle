import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._now = time.monotonic if now is None else now
        self._items = OrderedDict()

    def set(self, key, value):
        current = self._now()
        self._purge_expired(current)

        if self.max_size == 0:
            return

        self._items[key] = (value, current + self.ttl_seconds)
        self._items.move_to_end(key)

        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def get(self, key):
        try:
            value, expires_at = self._items[key]
        except KeyError:
            return None

        current = self._now()
        if current >= expires_at:
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return value

    def _purge_expired(self, current):
        for key, (_, expires_at) in list(self._items.items()):
            if current >= expires_at:
                del self._items[key]
