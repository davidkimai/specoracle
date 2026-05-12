# ttl_cache.py

"""A thread-unsafe LRU cache with a per-cache Time-To-Live (TTL) expiration policy."""

import collections
import time
from typing import Any, Callable, Optional


class TTLCache:
    """
    A dictionary-like, fixed-size cache with a Time-To-Live (TTL) for its entries.

    It evicts the least-recently-used (LRU) item when the cache is full.
    An item is considered expired if `current_time - insertion_time > ttl_seconds`.
    Expired items are removed upon access via `get`.

    This implementation is not thread-safe.
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
            max_size: The maximum number of items the cache can hold. Must be > 0.
            ttl_seconds: The time-to-live for each item in seconds. Must be >= 0.
            now: An optional callable that returns the current time as a float
                 (e.g., `time.time`). Used for testing. If None, `time.time`
                 is used.
        """
        if max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be a non-negative number")

        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.time
        self._cache = collections.OrderedDict()

    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieves an item from the cache.

        Returns the value if the key exists and has not expired, otherwise None.
        Accessing an item marks it as most-recently-used.
        If an item is accessed and found to be expired, it is removed from the
        cache.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value associated with the key, or None if the key is not found
            or the item has expired.
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        if self._now() - timestamp > self.ttl_seconds:
            # Entry has expired, remove it and return None.
            del self._cache[key]
            return None
        else:
            # Entry is valid, mark as most-recently-used and return value.
            self._cache.move_to_end(key)
            return value

    def set(self, key: Any, value: Any) -> None:
        """
        Adds or updates an item in the cache.

        Setting an item marks it as the most-recently-used.
        If the cache is full, the least-recently-used item is evicted before
        the new item is added.

        Args:
            key: The key of the item to set.
            value: The value of the item to set.
        """
        # If the key already exists, remove it to update its position and value.
        if key in self._cache:
            del self._cache[key]

        # If the cache is full, evict the least-recently-used item.
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = (value, self._now())
