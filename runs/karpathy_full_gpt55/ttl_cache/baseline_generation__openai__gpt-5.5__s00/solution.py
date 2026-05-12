import math
import operator
import time
from collections import OrderedDict
from typing import Any, Callable, Optional


class TTLCache:
    """A small least-recently-used cache with time-based expiration."""

    __slots__ = ("_max_size", "_ttl_seconds", "_now", "_items")

    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        try:
            max_size_value = operator.index(max_size)
        except TypeError as exc:
            raise TypeError("max_size must be an integer") from exc

        if max_size_value < 0:
            raise ValueError("max_size must be non-negative")

        try:
            ttl_value = float(ttl_seconds)
        except (TypeError, ValueError) as exc:
            raise TypeError("ttl_seconds must be a number") from exc

        if ttl_value < 0 or math.isnan(ttl_value):
            raise ValueError("ttl_seconds must be non-negative")

        if now is None:
            now_func = time.monotonic
        elif callable(now):
            now_func = now
        else:
            raise TypeError("now must be callable")

        self._max_size = max_size_value
        self._ttl_seconds = ttl_value
        self._now = now_func
        self._items: OrderedDict[Any, tuple[float, Any]] = OrderedDict()

    def set(self, key: Any, value: Any) -> None:
        """Store value for key, evicting expired and least-recently-used entries."""
        current_time = self._current_time()

        if self._max_size == 0:
            self._items.pop(key, None)
            self._purge_expired(current_time)
            return

        self._purge_expired(current_time)

        expires_at = current_time + self._ttl_seconds
        self._items[key] = (expires_at, value)
        self._items.move_to_end(key)

        while len(self._items) > self._max_size:
            self._items.popitem(last=False)

    def get(self, key: Any) -> Any:
        """Return the cached value for key, or None if absent or expired."""
        try:
            expires_at, value = self._items[key]
        except KeyError:
            return None

        current_time = self._current_time()
        if current_time >= expires_at:
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return value

    def __len__(self) -> int:
        self._purge_expired(self._current_time())
        return len(self._items)

    def __contains__(self, key: Any) -> bool:
        try:
            expires_at, _ = self._items[key]
        except KeyError:
            return False

        if self._current_time() >= expires_at:
            del self._items[key]
            return False

        return True

    def clear(self) -> None:
        self._items.clear()

    def _current_time(self) -> float:
        return float(self._now())

    def _purge_expired(self, current_time: float) -> None:
        expired_keys = [
            key for key, (expires_at, _) in self._items.items()
            if current_time >= expires_at
        ]
        for key in expired_keys:
            self._items.pop(key, None)
