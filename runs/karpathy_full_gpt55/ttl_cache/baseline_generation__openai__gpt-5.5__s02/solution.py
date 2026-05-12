import time
from collections import OrderedDict
from typing import Any, Callable, Optional


class TTLCache:
    """A small least-recently-used cache with per-entry time-to-live expiry."""

    def __init__(self, max_size: int, ttl_seconds: float, *, now: Optional[Callable[[], float]] = None):
        if not isinstance(max_size, int):
            raise TypeError("max_size must be an int")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self.max_size = max_size
        self.ttl_seconds = float(ttl_seconds)
        self._now = now if now is not None else time.monotonic
        self._items = OrderedDict()

    def set(self, key: Any, value: Any) -> None:
        current_time = self._now()
        self._purge_expired(current_time)

        if self.max_size == 0:
            return

        expires_at = current_time + self.ttl_seconds

        if key in self._items:
            del self._items[key]

        self._items[key] = (value, expires_at)

        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def get(self, key: Any) -> Any:
        current_time = self._now()

        try:
            value, expires_at = self._items[key]
        except KeyError:
            return None

        if current_time >= expires_at:
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return value

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        self._purge_expired(self._now())
        return len(self._items)

    def __contains__(self, key: Any) -> bool:
        return self.get(key) is not None

    def _purge_expired(self, current_time: float) -> None:
        expired_keys = [
            key
            for key, (_value, expires_at) in self._items.items()
            if current_time >= expires_at
        ]
        for key in expired_keys:
            self._items.pop(key, None)
