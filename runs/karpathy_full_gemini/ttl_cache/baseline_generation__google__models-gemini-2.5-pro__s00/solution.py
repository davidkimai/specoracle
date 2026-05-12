# ttl_cache.py

"""
A thread-unsafe, size-limited cache with TTL (Time-To-Live) and
LRU (Least-Recently-Used) eviction policies.
"""

import time
from typing import Callable, Generic, Optional, TypeVar

# Type variables for generic key/value pairs
KT = TypeVar('KT')
VT = TypeVar('VT')


class _Node(Generic[KT, VT]):
    """A node in the doubly linked list used by TTLCache."""
    __slots__ = ('key', 'value', 'timestamp', 'prev', 'next')

    def __init__(self, key: KT, value: VT, timestamp: float):
        self.key: KT = key
        self.value: VT = value
        self.timestamp: float = timestamp
        self.prev: Optional['_Node[KT, VT]'] = None
        self.next: Optional['_Node[KT, VT]'] = None


class TTLCache(Generic[KT, VT]):
    """
    A thread-unsafe, size-limited cache with TTL (Time-To-Live) and
    LRU (Least-Recently-Used) eviction policies.

    When the cache exceeds its maximum size, the least recently used item is
    evicted. When an item is accessed via `get`, it is considered "used".
    An item is considered expired if the current time is greater than its
    creation/last-update time plus the TTL. Expired items are removed upon
    access.
    """

    def __init__(
        self,
        max_size: int,
        ttl
