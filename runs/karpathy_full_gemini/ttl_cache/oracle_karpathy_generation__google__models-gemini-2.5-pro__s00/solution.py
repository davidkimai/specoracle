# ttl_cache.py

"""
A thread-unsafe Time-To-Live (TTL) cache with a Least-Recently-Used (LRU)
eviction policy.
"""

import collections
import time
from typing import Any, Callable, Optional, Tuple


class TTLCache:
    """
    A dictionary-like cache object that stores a limited number of items,
    each with a time-to-live (TTL).

    When the cache is full, it evicts the least recently used (LRU) item
    to make space for a new one.

    When an item is accessed, it is checked for expiration. Expired items
    are removed and treated as a cache miss. This is a thread-unsafe
    implementation.
    """

    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a TTLCache instance.

        Args:
            max_size: The maximum number of items to store in the cache.
            ttl_seconds: The time-to-live for each item, in seconds.
            now: An optional callable that returns the current time as a float
                 (e.g., time.time). Used for testing. Defaults to time.time.
        """
        if max_size <= 0:
            raise ValueError("max_size must be a positive integer.")
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be a non-negative number.")

        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.time
        self._cache: collections.OrderedDict[Any, Tuple[Any, float]] = (
            collections.OrderedDict()
        )

    def _is_expired(self, timestamp: float) -> bool:
        """Checks if a timestamp is older than the TTL."""
        return self._now() - timestamp > self._ttl_seconds

    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieves an item from the cache.

        If the item is found and has not expired, its value is returned.
        The item is also marked as the most recently used.

        If the item is not found or has expired, it is removed from the cache
        and None is returned.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value of the item, or None if the item is not in the cache
            or has expired.
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        if self._is_expired(timestamp):
            del self._cache[key]
            return None

        # Mark as most recently used
        self._cache.move_to_end(key)
        return value

    def set(self, key: Any, value: Any) -> None:
        """
        Adds or updates an item in the cache.

        If the key already exists, its value and timestamp are updated, and it
        is marked as the most recently used.

        If the key does not exist and the cache is full, the least recently
        used item is evicted before the new item is added.

        Args:
            key: The key of the item to store.
            value: The value of the item to store.
        """
        if key in self._cache:
            # Update existing item's value and timestamp
            self._cache[key] = (value, self._now())
            # Mark as most recently used
            self._cache.move_to_end(key)
        else:
            # Evict if capacity is reached
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            # Add new item
            self._cache[key] = (value, self._now())
