import time
from collections import OrderedDict


class TTLCache:
    """A small in-memory TTL cache with least-recently-used eviction.

    Assumptions:
    - now, if provided, is a zero-argument callable returning a time in seconds.
    - ttl_seconds <= 0 makes newly set entries expire immediately.
    - max_size <= 0 means no entries are retained.
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._now = time.monotonic if now is None else now
        self._items = OrderedDict()

    def set(self, key, value):
        if self.max_size <= 0:
            self._items.clear()
            return

        current = self._now()
        self._remove_expired(current)

        expires_at = current + self.ttl_seconds
        if current >= expires_at:
            self._items.pop(key, None)
            return

        self._items[key] = (value, expires_at)
        self._items.move_to_end(key)

        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def get(self, key):
        item = self._items.get(key)
        if item is None:
            return None

        current = self._now()
        value, expires_at = item
        if current >= expires_at:
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return value

    def _remove_expired(self, current):
        expired_keys = [
            key
            for key, (_, expires_at) in self._items.items()
            if current >= expires_at
        ]
        for key in expired_keys:
            self._items.pop(key, None)
