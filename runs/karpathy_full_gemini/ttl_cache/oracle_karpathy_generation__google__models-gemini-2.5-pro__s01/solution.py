import collections
import time
from typing import Any, Callable, Optional


class TTLCache:
    """
    A thread-unsafe, in-memory cache that evicts the least-recently-used (LRU)
    item when the `max_size` is exceeded, and invalidates items after a
    specified time-to-live (TTL).
    """

    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        *,
        now: Optional[Callable[[], float]] = None
    ):
        """
        Initializes a TTLCache instance.

        Args:
            max_size: The maximum number of items the cache can hold. Must be
                      a positive integer.
            ttl_seconds: The time-to-live for each item in seconds. Must be a
                         non-negative number.
            now: An optional callable that returns the current time as a float
                 (e.g., `time.time`). Used for testing. Defaults to `time.time`.

        Raises:
            ValueError: If `max_size` is not a positive integer or
                        `ttl_seconds` is negative.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be a non-negative number")

        self._max_size: int = max_size
        self._ttl_seconds: float = ttl_seconds
        self._now: Callable[[], float] = now if now is not None else time.time
        self._cache: collections.OrderedDict[Any, tuple[Any, float]] = (
            collections.OrderedDict()
        )

    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieves an item from the cache.

        If the item is found and has not expired, it is returned and marked as
        the most recently used item.

        If the item is not found or has expired, it is removed from the cache
        and `None` is returned.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value of the item, or `None` if the item is not found or has
            expired.
        """
        try:
            value, expires_at = self._cache[key]
        except KeyError:
            return None

        if self._now() > expires_at:
            # Item has expired, remove it from the cache.
            del self._cache[key]
            return None

        # Item is valid, mark it as most recently used and return its value.
        self._cache.move_to_end(key)
        return value

    def set(self, key: Any, value: Any) -> None:
        """
        Adds or updates an item in the cache.

        The item is stored with a new expiration time and marked as the most
        recently used item.

        If adding the item causes the cache to exceed `max_size`, the
        least-recently-used item is evicted.

        Args:
            key: The key of the item to store.
            value: The value of the item to store.
        """
        expires_at = self._now() + self._ttl_seconds

        # Add or update the item and mark it as most recently used.
        self._cache[key] = (value, expires_at)
        self._cache.move_to_end(key)

        # Evict the least recently used item if the cache is oversized.
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
