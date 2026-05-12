from collections import OrderedDict
import time
from typing import Any, Callable, Optional


class TTLCache:
    """A small least-recently-used cache with time-to-live expiration."""

    def __init__(self, max_size: int, ttl_seconds: float, *, now: Optional[Callable[[], float]] = None):
        if not isinstance(max_size, int):
            raise TypeError("max_size must be an int")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if not callable(now) and now is not None:
            raise TypeError("now must be callable")

        self.max_size = max_size
        self.ttl_seconds = float(ttl_seconds)
        self._now = time.monotonic if now is None else now
        self._items = OrderedDict()

    def set(self, key: Any, value: Any) -> None:
        """Store value for key, refreshing its TTL and LRU position."""
        if self.max_size == 0:
            self._items.clear()
            return

        current_time = self._now()
        expires_at = current_time + self.ttl_seconds

        if key in self._items:
            del self._items[key]

        self._items[key] = (value, expires_at)
        self._purge_expired(current_time)

        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def get(self, key: Any) -> Any:
        """Return the stored value, or None if absent or expired."""
        item = self._items.get(key)
        if item is None:
            return None

        value, expires_at = item
        if expires_at <= self._now():
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return value

    def _purge_expired(self, current_time: Optional[float] = None) -> None:
        if current_time is None:
            current_time = self._now()

        expired_keys = [
            key for key, (_, expires_at) in self._items.items()
            if expires_at <= current_time
        ]
        for key in expired_keys:
            self._items.pop(key, None)

    def __len__(self) -> int:
        self._purge_expired()
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
