# ttl_cache.py
"""
A thread-safe Time-To-Live (TTL) cache with a Least-Recently-Used (LRU)
eviction policy.
"""

import threading
import time
from typing import Callable, Dict, Generic, Optional, Tuple, TypeVar

# Type variables for generic key and value types
K = TypeVar('K')
V = TypeVar('V')


class TTLCache(Generic[K, V]):
    """
    A thread-safe Time-To-Live (TTL) cache with a Least-Recently-Used (LRU)
    eviction policy.

    This cache stores a limited number of items, each with a specific
    time-to-live. When the cache is full, it evicts the least recently used
    item to make space. Items are also considered expired and removed if their
    TTL has passed.

    The implementation relies on the insertion order of standard Python
    dictionaries, a feature guaranteed since Python 3.7.

    This class is thread-safe.
    """

    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        *,
        now: Optional[Callable[[], float]] = None
    ):
        """
        Initializes the TTLCache.

        Args:
            max_size: The maximum number of items the cache can hold.
                      Must be a positive integer.
            ttl_seconds: The time-to-live for each item in seconds.
                         Must be a positive number.
            now: An optional callable that returns the current time as a float.
                 If None, `time.monotonic` is used. This is useful for testing.

        Raises:
            ValueError: If `max_size` or `ttl_seconds` are not positive.
        """
        if max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be a positive number")

        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.monotonic
        self._cache: Dict[K, Tuple[V, float]] = {}
        self._lock = threading.RLock()

    def get(self, key: K) -> Optional[V]:
        """
        Retrieves an item from the cache.

        If the item is found and not expired, it is returned and marked as
        recently used. If the item is not found or has expired, None is
        returned and the item is removed from the cache if it existed.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value associated with the key, or None if the key is not
            in the cache or the item has expired.
        """
        with self._lock:
            if key not in self._cache:
                return None

            value, expiration_time = self._cache[key]

            if self._now() > expiration_time:
                # Entry has expired, remove it.
                del self._cache[key]
                return None

            # Entry is valid. Mark as recently used by moving it to the end.
            del self._cache[key]
            self._cache[key] = (value, expiration_time)

            return value

    def set(self, key: K, value: V) -> None:
        """
        Adds or updates an item in the cache.

        When an item is added, it is given a new TTL. If the cache is full,
        the least recently used item is evicted. If the key already exists,
        its value and TTL are updated, and it is marked as recently used.

        Args:
            key: The key of the item to store.
            value: The value of the item to store.
        """
        with self._lock:
            # If the key already exists, remove it to update its position.
            if key in self._cache:
                del self._cache[key]

            # Add the new item with its expiration time.
            expiration_time = self._now() + self._ttl_seconds
            self._cache[key] = (value, expiration_time)

            # Enforce max_size by evicting the least recently used item.
            if len(self._cache) > self._max_size:
                # `next(iter(self._cache))` gets the first key inserted,
                # which is the LRU item in Python 3.7+.
                lru_key = next(iter(self._cache))
                del self._cache[lru_key]
