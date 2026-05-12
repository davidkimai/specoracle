"""
TTLCache: A cache with time-to-live expiration and LRU eviction policy.
"""

import time
from collections import OrderedDict


class TTLCache:
    """
    A cache that evicts entries based on time-to-live (TTL) expiration
    and least-recently-used (LRU) policy when max_size is exceeded.

    Parameters
    ----------
    max_size : int
        Maximum number of entries the cache can hold.
    ttl_seconds : float
        Time in seconds before an entry expires.
    now : callable, optional
        A callable that returns the current time as a float (seconds).
        Defaults to time.monotonic. Useful for testing.
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        # OrderedDict stores: key -> (value, expiry_time)
        # Most recently used at the end (move_to_end on access/set)
        self._cache: OrderedDict = OrderedDict()

    def _is_expired(self, expiry_time: float) -> bool:
        return self._now() >= expiry_time

    def _purge_expired(self):
        """Remove all expired entries."""
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if self._is_expired(expiry)
        ]
        for key in expired_keys:
            del self._cache[key]

    def set(self, key, value) -> None:
        """
        Store a value in the cache under the given key.

        If the key already exists, update its value and reset its TTL.
        If the cache is full after insertion, evict the least-recently-used entry.
        """
        expiry_time = self._now() + self._ttl

        if key in self._cache:
            # Update existing entry and move to end (most recently used)
            self._cache[key] = (value, expiry_time)
            self._cache.move_to_end(key)
        else:
            # Before inserting, purge expired entries to free space
            if len(self._cache) >= self._max_size:
                self._purge_expired()

            # If still at capacity after purging, evict LRU entry
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)  # Remove least recently used (front)

            self._cache[key] = (value, expiry_time)
            self._cache.move_to_end(key)

    def get(self, key):
        """
        Retrieve a value from the cache.

        Returns the value if the key exists and has not expired.
        Returns None if the key is absent or has expired.
        """
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]

        if self._is_expired(expiry_time):
            del self._cache[key]
            return None

        # Move to end to mark as recently used
        self._cache.move_to_end(key)
        return value

    def __len__(self) -> int:
        """Return the number of non-expired entries currently in the cache."""
        self._purge_expired()
        return len(self._cache)

    def __contains__(self, key) -> bool:
        """Check if a key exists in the cache and has not expired."""
        return self.get(key) is not None

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._cache.clear()
