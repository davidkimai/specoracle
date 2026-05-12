"""A thread-unsafe TTL cache with a least-recently-used eviction policy."""

import collections
import time
from typing import Callable, Generic, Optional, Tuple, TypeVar

# Type variables for generic cache keys and values.
K = TypeVar("K")
V = TypeVar("V")


def _validate_constructor_args(max_size: int, ttl_seconds: float) -> None:
    """Raise ValueError for invalid TTLCache constructor arguments."""
    if not isinstance(max_size, int) or max_size <= 0:
        raise ValueError("max_size must be a positive integer")

    if not isinstance(ttl_seconds, (int, float)) or ttl_seconds < 0:
        raise ValueError("ttl_seconds must be a non-negative number")


class TTLCache(Generic[K, V]):
    """
    A thread-unsafe, in-memory cache with a Time-To-Live (TTL) and a
    Least-Recently-Used (LRU) eviction policy.

    Items are evicted in two ways:
    1. When an item is accessed via `get` but its TTL has expired.
    2. When the cache is full and a new item is `set`, the
       least-recently-used item is removed.
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
            max_size: The maximum number of items the cache can hold.
            ttl_seconds: The time-to-live for each item in seconds.
            now: A callable that returns the current time as a float.
                 Defaults to time.monotonic. This is useful for testing.

        Raises:
            ValueError: If max_size is not a positive integer or
                        ttl_seconds is a negative number.
        """
        _validate_constructor_args(max_size, ttl_seconds)

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        self._cache: collections.OrderedDict[K, Tuple[V, float]] = (
            collections.OrderedDict()
        )

    def get(self, key: K) -> Optional[V]:
        """
        Retrieves an item from the cache.

        Returns the item's value if it exists and has not expired,
        otherwise returns None. Accessing an item marks it as
        most-recently-used.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value of the item, or None if not found or expired.
        """
        try:
            value, expiration_time = self._cache[key]
        except KeyError:
            return None

        if self._now() > expiration_time:
            # Item has expired, remove it lazily and return None.
            del self._cache[key]
            return None

        # Item is valid, mark it as most-recently-used and return its value.
        self._cache.move_to_end(key)
        return value

    def set(self, key: K, value: V) -> None:
        """
        Adds or updates an item in the cache.

        Setting an item marks it as the most-recently-used. If adding the
        item causes the cache to exceed its maximum size, the
        least-recently-used item is evicted.

        Args:
            key: The key of the item to set.
            value: The value of the item.
        """
        expiration_time = self._now() + self._ttl
        self._cache[key] = (value, expiration_time)
        self._cache.move_to_end(key)

        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
