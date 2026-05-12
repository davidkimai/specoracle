"""
TTLCache: A time-to-live cache with LRU eviction policy.
"""

import time
from collections import OrderedDict


class TTLCache:
    """
    A cache with a maximum size and time-to-live (TTL) for entries.
    
    - Entries expire after ttl_seconds.
    - When max_size is exceeded, the least-recently-used entry is evicted.
    - The `now` parameter is a callable that returns the current time
      (defaults to time.monotonic). Useful for testing.
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic

        # OrderedDict maps key -> (value, expiry_time)
        # Most-recently-used items are at the end (right side).
        self._cache: OrderedDict = OrderedDict()

    def set(self, key, value) -> None:
        """Store a value in the cache, evicting LRU entry if necessary."""
        expiry = self._now() + self._ttl

        if key in self._cache:
            # Update existing entry and move to end (most recently used)
            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)
        else:
            # Evict LRU entries that are expired first, then oldest if needed
            self._evict_expired()

            if len(self._cache) >= self._max_size:
                # Evict the least-recently-used entry (leftmost)
                self._cache.popitem(last=False)

            self._cache[key] = (value, expiry)

    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Returns None if the key is absent or the entry has expired.
        Accessing a valid entry marks it as most-recently-used.
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        if self._now() >= expiry:
            # Entry has expired; remove it
            del self._cache[key]
            return None

        # Mark as recently used
        self._cache.move_to_end(key)
        return value

    def _evict_expired(self) -> None:
        """Remove all expired entries from the cache."""
        current_time = self._now()
        expired_keys = [
            k for k, (v, expiry) in self._cache.items()
            if current_time >= expiry
        ]
        for k in expired_keys:
            del self._cache[k]

    def __len__(self) -> int:
        """Return the number of non-expired entries currently in the cache."""
        self._evict_expired()
        return len(self._cache)

    def __contains__(self, key) -> bool:
        """Return True if key exists and has not expired."""
        return self.get(key) is not None

    def __repr__(self) -> str:
        return (
            f"TTLCache(max_size={self._max_size}, ttl_seconds={self._ttl}, "
            f"current_size={len(self._cache)})"
        )
