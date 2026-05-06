"""
TTLCache: A cache with time-to-live expiration and LRU eviction policy.
"""

import time
from collections import OrderedDict


class TTLCache:
    """
    A cache that supports:
    - Time-to-live (TTL) expiration for each entry
    - LRU (Least Recently Used) eviction when max_size is exceeded
    
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
        self._ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.monotonic

        # OrderedDict maintains insertion/access order for LRU tracking.
        # Each value is a tuple of (value, expiry_timestamp).
        self._cache: OrderedDict = OrderedDict()

    def _is_expired(self, expiry: float) -> bool:
        """Return True if the entry has expired."""
        return self._now() >= expiry

    def _evict_expired(self):
        """Remove all expired entries from the cache."""
        current_time = self._now()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time >= expiry
        ]
        for key in expired_keys:
            del self._cache[key]

    def set(self, key, value):
        """
        Store a value in the cache.
        
        If the key already exists, update it and mark it as recently used.
        If the cache is at max capacity after insertion, evict the LRU entry.
        
        Parameters
        ----------
        key : hashable
            The cache key.
        value : any
            The value to store.
        """
        expiry = self._now() + self._ttl_seconds

        if key in self._cache:
            # Update existing entry and move to end (most recently used)
            self._cache.move_to_end(key)
            self._cache[key] = (value, expiry)
        else:
            # Insert new entry
            self._cache[key] = (value, expiry)

            # Evict LRU entries if over capacity
            # First try to remove expired entries to free space
            if len(self._cache) > self._max_size:
                self._evict_expired()

            # If still over capacity, remove the least recently used entry
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Returns None if the key is absent or if the entry has expired.
        Accessing a valid entry marks it as recently used.
        
        Parameters
        ----------
        key : hashable
            The cache key to look up.
        
        Returns
        -------
        The cached value, or None if absent or expired.
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        if self._is_expired(expiry):
            # Remove expired entry
            del self._cache[key]
            return None

        # Move to end to mark as recently used
        self._cache.move_to_end(key)
        return value

    def warm(self, initial: dict):
        """
        Pre-populate the cache from a dictionary using the current time.

        Entries are inserted in iteration order. If the number of entries in
        ``initial`` exceeds ``max_size``, only the last ``max_size`` items
        (by iteration order) are retained, matching the behaviour of
        successive ``set`` calls which evict the least-recently-used entry.

        Parameters
        ----------
        initial : dict
            Mapping of key → value pairs to load into the cache.
        """
        for key, value in initial.items():
            self.set(key, value)

    def __len__(self) -> int:
        """Return the number of entries currently in the cache (including potentially expired ones)."""
        return len(self._cache)

    def __contains__(self, key) -> bool:
        """Check if a key exists in the cache and is not expired."""
        return self.get(key) is not None

    def clear(self):
        """Remove all entries from the cache."""
        self._cache.clear()

    def __repr__(self) -> str:
        return (
            f"TTLCache(max_size={self._max_size}, "
            f"ttl_seconds={self._ttl_seconds}, "
            f"current_size={len(self._cache)})"
        )
