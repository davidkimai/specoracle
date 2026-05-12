from __future__ import annotations

import math
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class _CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        self._max_size = _validate_max_size(max_size)
        self._ttl_seconds = _validate_ttl_seconds(ttl_seconds)
        self._now = time.monotonic if now is None else _validate_now(now)
        self._items: OrderedDict[Any, _CacheEntry] = OrderedDict()

    def set(self, key: Any, value: Any) -> None:
        current_time = self._current_time()
        self._remove_expired(current_time)

        self._items[key] = _CacheEntry(
            value=value,
            expires_at=current_time + self._ttl_seconds,
        )
        self._items.move_to_end(key)
        self._evict_over_limit()

    def get(self, key: Any) -> Any:
        entry = self._items.get(key)
        if entry is None:
            return None

        current_time = self._current_time()
        if _is_expired(entry, current_time):
            del self._items[key]
            return None

        self._items.move_to_end(key)
        return entry.value

    def __len__(self) -> int:
        self._remove_expired(self._current_time())
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()

    def _current_time(self) -> float:
        value = self._now()
        try:
            current_time = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("now() must return a finite number") from exc

        if not math.isfinite(current_time):
            raise ValueError("now() must return a finite number")

        return current_time

    def _remove_expired(self, current_time: float) -> None:
        expired_keys = [
            key
            for key, entry in self._items.items()
            if _is_expired(entry, current_time)
        ]
        for key in expired_keys:
            del self._items[key]

    def _evict_over_limit(self) -> None:
        while len(self._items) > self._max_size:
            self._items.popitem(last=False)


def _validate_max_size(max_size: int) -> int:
    if isinstance(max_size, bool) or not isinstance(max_size, int):
        raise TypeError("max_size must be an integer")

    if max_size < 1:
        raise ValueError("max_size must be at least 1")

    return max_size


def _validate_ttl_seconds(ttl_seconds: float) -> float:
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, (int, float)):
        raise TypeError("ttl_seconds must be a finite number")

    ttl = float(ttl_seconds)
    if not math.isfinite(ttl):
        raise ValueError("ttl_seconds must be a finite number")

    if ttl < 0:
        raise ValueError("ttl_seconds must be non-negative")

    return ttl


def _validate_now(now: Callable[[], float]) -> Callable[[], float]:
    if not callable(now):
        raise TypeError("now must be callable")

    return now


def _is_expired(entry: _CacheEntry, current_time: float) -> bool:
    return current_time >= entry.expires_at
