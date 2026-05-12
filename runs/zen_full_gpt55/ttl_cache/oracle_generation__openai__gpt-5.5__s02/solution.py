from collections import OrderedDict
from dataclasses import dataclass
import math
from numbers import Real
import time
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class _Entry:
    value: Any
    expires_at: float


def _validate_max_size(max_size: int) -> int:
    if isinstance(max_size, bool) or not isinstance(max_size, int):
        raise TypeError("max_size must be an integer")
    if max_size < 0:
        raise ValueError("max_size must be non-negative")
    return max_size


def _validate_ttl_seconds(ttl_seconds: float) -> float:
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, Real):
        raise TypeError("ttl_seconds must be a real number")

    ttl = float(ttl_seconds)
    if not math.isfinite(ttl):
        raise ValueError("ttl_seconds must be finite")
    if ttl < 0:
        raise ValueError("ttl_seconds must be non-negative")
    return ttl


def _validate_now(now: Optional[Callable[[], float]]) -> Callable[[], float]:
    if now is None:
        return time.monotonic
    if not callable(now):
        raise TypeError("now must be callable")
    return now


class TTLCache:
    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        self._max_size = _validate_max_size(max_size)
        self._ttl_seconds = _validate_ttl_seconds(ttl_seconds)
        self._now = _validate_now(now)
        self._items = OrderedDict()

    def set(self, key, value) -> None:
        current_time = self._current_time()
        self._items[key] = _Entry(value=value, expires_at=current_time + self._ttl_seconds)
        self._items.move_to_end(key)
        self._purge_expired(current_time)
        self._evict_lru_entries()

    def get(self, key):
        current_time = self._current_time()
        entry = self._items.get(key)
        if entry is None:
            return None

        if entry.expires_at <= current_time:
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return entry.value

    def _current_time(self) -> float:
        value = self._now()
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError("now() must return a real number")

        current_time = float(value)
        if not math.isfinite(current_time):
            raise ValueError("now() must return a finite number")
        return current_time

    def _purge_expired(self, current_time: float) -> None:
        expired_keys = [
            key
            for key, entry in self._items.items()
            if entry.expires_at <= current_time
        ]
        for key in expired_keys:
            del self._items[key]

    def _evict_lru_entries(self) -> None:
        while len(self._items) > self._max_size:
            self._items.popitem(last=False)
