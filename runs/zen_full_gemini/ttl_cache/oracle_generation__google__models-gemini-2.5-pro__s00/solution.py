import time
from collections import OrderedDict
from typing import Callable, Generic, Optional, TypeVar

K = TypeVar('K')
V = TypeVar('V')


class TTLCache(Generic[K, V]):
    """
    A thread-unsafe Time-To-Live (TTL) cache with a Least-Recently-Used (LRU)
    eviction policy.
    """

    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes the TTLCache.

        Args:
            max_size: The maximum number of items the cache can hold. Must be
                      a positive integer.
            ttl_seconds: The time-to-live for each item in seconds. Must be
                         a positive number.
            now: An optional callable that returns the current time as a float.
                 If None, `time.time` is used. This is useful for testing.

        Raises:
            ValueError: If max_size or ttl_seconds are not valid.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be a positive number")

        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.time
        self._cache: OrderedDict[K, tuple[V, float]] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        """
        Retrieves an item from the cache.

        Returns the value if the key exists and has not expired, otherwise None.
        Accessing an item marks it as recently used. Expired items found during
        access are removed from the cache.

        Args:
            key: The key of the item to retrieve.
        """
        if key not in self._cache:
            return None

        value, expiration_time = self._cache[key]

        if self._now() > expiration_time:
            # Item has expired. Remove it and signal a cache miss.
            del self._cache[key]
            return None

        # Item is valid. Mark it as recently used and return the value.
        self._cache.move_to_end(key)
        return value

    def set(self, key: K, value: V) -> None:
        """
        Adds or updates an item in the cache.

        If adding a new item causes the cache to exceed its maximum size, the
        least recently used item is evicted. Setting an item marks it as the
        most recently used.

        Args:
            key: The key of the item to set.
            value: The value of the item.
        """
        expiration_time = self._now() + self._ttl_seconds
        self._cache[key] = (value, expiration_time)
        self._cache.move_to_end(key)

        self._evict_if_over_size()

    def _evict_if_over_size(self) -> None:
        """Evicts the least recently used item if the cache is over size."""
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
