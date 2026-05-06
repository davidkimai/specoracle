"""TTL Cache implementation with LRU eviction policy."""

import time
from collections import OrderedDict


class TTLCache:
    """A cache with time-to-live expiration and LRU eviction.
    
    Args:
        max_size: Maximum number of entries to store.
        ttl_seconds: Time-to-live in seconds for each entry.
        now: Optional callable that returns the current time (defaults to time.monotonic).
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.monotonic
        # OrderedDict maps key -> (value, expiry_time)
        # Most recently used at the end (move_to_end with last=True)
        self._cache: OrderedDict = OrderedDict()

    def _is_expired(self, expiry_time: float) -> bool:
        return self._now() >= expiry_time

    def _evict_expired(self):
        """Remove all expired entries."""
        current_time = self._now()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time >= expiry
        ]
        for key in expired_keys:
            del self._cache[key]

    def set(self, key, value) -> None:
        """Store a value in the cache.
        
        If the key already exists, update its value and reset its TTL.
        If the cache is full after adding, evict the least-recently-used entry.
        """
        expiry_time = self._now() + self._ttl_seconds
        
        if key in self._cache:
            # Update existing entry and move to end (most recently used)
            self._cache[key] = (value, expiry_time)
            self._cache.move_to_end(key, last=True)
        else:
            # Add new entry
            self._cache[key] = (value, expiry_time)
            self._cache.move_to_end(key, last=True)
            
            # Evict if over capacity: first try expired entries, then LRU
            if len(self._cache) > self._max_size:
                # Try to evict expired entries first
                self._evict_expired()
                
                # If still over capacity, evict least recently used
                while len(self._cache) > self._max_size:
                    self._cache.popitem(last=False)

    def get(self, key):
        """Retrieve a value from the cache.
        
        Returns the value if present and not expired, otherwise None.
        Accessing a valid entry marks it as recently used.
        """
        if key not in self._cache:
            return None
        
        value, expiry_time = self._cache[key]
        
        if self._is_expired(expiry_time):
            del self._cache[key]
            return None
        
        # Move to end to mark as recently used
        self._cache.move_to_end(key, last=True)
        return value

    def __len__(self) -> int:
        """Return the number of entries (including potentially expired ones)."""
        return len(self._cache)

    def __contains__(self, key) -> bool:
        """Check if a key is present and not expired."""
        return self.get(key) is not None

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._cache.clear()
