from collections import OrderedDict
import math
from numbers import Real
import time


class TTLCache:
    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        self._max_size = self._validate_max_size(max_size)
        self._ttl_seconds = self._validate_ttl_seconds(ttl_seconds)
        self._now = time.monotonic if now is None else self._validate_now(now)
        self._items = OrderedDict()

    def set(self, key, value):
        current_time = self._current_time()
        expires_at = current_time + self._ttl_seconds

        if key in self._items:
            del self._items[key]

        self._items[key] = (value, expires_at)
        self._remove_expired(current_time)
        self._evict_to_size()

    def get(self, key):
        current_time = self._current_time()

        try:
            value, expires_at = self._items[key]
        except KeyError:
            return None

        if self._is_expired(expires_at, current_time):
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return value

    @staticmethod
    def _validate_max_size(max_size):
        if isinstance(max_size, bool) or not isinstance(max_size, int):
            raise TypeError("max_size must be an integer")
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        return max_size

    @staticmethod
    def _validate_ttl_seconds(ttl_seconds):
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, Real):
            raise TypeError("ttl_seconds must be a real number")
        ttl = float(ttl_seconds)
        if not math.isfinite(ttl):
            raise ValueError("ttl_seconds must be finite")
        if ttl < 0:
            raise ValueError("ttl_seconds must be non-negative")
        return ttl

    @staticmethod
    def _validate_now(now):
        if not callable(now):
            raise TypeError("now must be callable")
        return now

    def _current_time(self):
        current_time = self._now()
        if isinstance(current_time, bool) or not isinstance(current_time, Real):
            raise TypeError("now() must return a real number")
        current_time = float(current_time)
        if not math.isfinite(current_time):
            raise ValueError("now() must return a finite number")
        return current_time

    @staticmethod
    def _is_expired(expires_at, current_time):
        return current_time >= expires_at

    def _remove_expired(self, current_time):
        expired_keys = [
            key
            for key, (_, expires_at) in self._items.items()
            if self._is_expired(expires_at, current_time)
        ]
        for key in expired_keys:
            del self._items[key]

    def _evict_to_size(self):
        while len(self._items) > self._max_size:
            self._items.popitem(last=False)
