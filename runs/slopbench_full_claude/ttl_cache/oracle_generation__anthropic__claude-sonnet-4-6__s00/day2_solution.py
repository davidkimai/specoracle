"""
TTLCache: a time-aware LRU cache with configurable max size and TTL.
"""

import time
from collections import OrderedDict


class TTLCache:
    """Cache with least-recently-used eviction and per-entry time-to-live."""

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError(f"max_size must be at least 1, got {max_size!r}")
        if ttl_seconds <= 0:
            raise ValueError(f"ttl_seconds must be positive, got {ttl_seconds!r}")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        # Maps key -> (value, expiry_time); ordered by recency of access.
        self._store: OrderedDict = OrderedDict()

    def _current_time(self) -> float:
        return self._now()

    def _is_expired(self, expiry: float) -> bool:
        return self._current_time() >= expiry

    def set(self, key, value) -> None:
        """Store value under key, evicting LRU entry if capacity is exceeded."""
        expiry = self._current_time() + self._ttl

        if key in self._store:
            # Remove so we can re-insert at the end (most-recent position).
            self._store.pop(key)

        self._store[key] = (value, expiry)

        # Evict LRU entries until within capacity.
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def get(self, key):
        """Return the value for key, or None if absent or expired."""
        if key not in self._store:
            return None

        value, expiry = self._store[key]

        if self._is_expired(expiry):
            del self._store[key]
            return None

        # Move to most-recent position.
        self._store.move_to_end(key)
        return value

    def warm(self, initial: dict) -> None:
        """Pre-populate the cache from a dict using the current time.

        Entries are inserted in iteration order; max_size is respected by
        keeping only the latest inserted entries (LRU eviction applies).
        """
        for key, value in initial.items():
            self.set(key, value)
