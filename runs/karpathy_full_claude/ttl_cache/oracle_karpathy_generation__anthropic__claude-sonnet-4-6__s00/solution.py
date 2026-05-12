import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        self._cache = OrderedDict()  # key -> (value, expiry)

    def set(self, key, value):
        expiry = self._now() + self._ttl
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, expiry)
        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def get(self, key):
        if key not in self._cache:
            return None
        value, expiry = self._cache[key]
        if self._now() >= expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value
