"""TTLCache: a time-aware LRU cache."""

import time
from collections import OrderedDict


class TTLCache:
    """A cache with a maximum size (LRU eviction) and per-entry TTL."""

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        # OrderedDict preserves insertion/access order for LRU tracking.
        # Values stored as (value, expiry_timestamp).
        self._store: OrderedDict = OrderedDict()

    def set(self, key, value) -> None:
        """Store *value* under *key*, resetting its TTL."""
        expiry = self._now() + self._ttl
        if key in self._store:
            # Move to end (most recently used).
            self._store.move_to_end(key)
        self._store[key] = (value, expiry)
        # Evict LRU entries until we are within max_size.
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def get(self, key):
        """Return the cached value for *key*, or None if absent or expired."""
        if key not in self._store:
            return None
        value, expiry = self._store[key]
        if self._now() >= expiry:
            # Entry has expired; remove it.
            del self._store[key]
            return None
        # Mark as recently used.
        self._store.move_to_end(key)
        return value

    def __len__(self) -> int:
        """Return the number of entries currently in the cache (including potentially expired ones)."""
        return len(self._store)

    def __contains__(self, key) -> bool:
        """Return True if *key* is present and not expired."""
        return self.get(key) is not None
