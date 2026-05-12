# -*- coding: utf-8 -*-
"""
A thread-unsafe, size-limited cache with a Time-To-Live (TTL) for its entries.
"""

import time
from typing import Callable, Generic, Optional, TypeVar

# Type variables for generic cache keys and values
KT = TypeVar("KT")
VT = TypeVar("VT")


class _Node(Generic[KT, VT]):
    """A node in the doubly linked list used by the TTLCache."""

    def __init__(
        self,
        key: KT,
        value: VT,
        expires_at: float,
        prev: Optional["_Node[KT, VT]"] = None,
        next: Optional["_Node[KT, VT]"] = None,
    ):
        self.key = key
        self.value = value
        self.expires_at = expires_at
        self.prev = prev
        self.next = next


class TTLCache(Generic[KT, VT]):
    """
    A thread-unsafe, size-limited cache with a Time-To-Live (TTL).

    When the cache exceeds its maximum size, it evicts the least-recently-used
    (LRU) entry. Entries are also considered invalid if their TTL has expired.
    The LRU and TTL policies are managed through a combination of a dictionary
    and a doubly linked list.
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
            max_size: The maximum number of entries the cache can hold.
            ttl_seconds: The time-to-live for each entry, in seconds.
            now: An optional callable that returns the current time as a float.
                 If None, `time.time` is used. This is useful for testing.

        Raises:
            ValueError: If max_size or ttl_seconds are not positive numbers.
        """
        if max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if not ttl_seconds > 0:
            raise ValueError("ttl_seconds must be a positive number")

        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._now = now if now is not None else time.time

        self._cache: dict[KT, _Node[KT, VT]] = {}
        # Sentinel nodes to simplify list manipulation logic
        self._head: _Node[KT, VT] = _Node(None, None, 0.0)  # type: ignore
        self._tail: _Node[KT, VT] = _Node(None, None, 0.0)  # type: ignore
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove_node(self, node: _Node[KT, VT]) -> None:
        """Removes a node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_head(self, node: _Node[KT, VT]) -> None:
        """Adds a node to the front (head) of the linked list."""
        node.next = self._head.next
        node.prev = self._head
        if self._head.next:
            self._head.next.prev = node
        self._head.next = node

    def _move_to_head(self, node: _Node[KT, VT]) -> None:
        """Moves an existing node to the head of the list."""
        self._remove_node(node)
        self._add_to_head(node)

    def _is_expired(self, node: _Node[KT, VT]) -> bool:
        """Checks if a node has expired."""
        return self._now() > node.expires_at

    def get(self, key: KT) -> Optional[VT]:
        """
        Retrieves a value from the cache.

        Returns the value if the key exists and has not expired, otherwise None.
        Accessing an entry marks it as the most recently used. If the entry
        is found to be expired, it is evicted from the cache.

        Args:
            key: The key of the entry to retrieve.

        Returns:
            The value associated with the key, or None if the key is not
            found or the entry has expired.
        """
        node = self._cache.get(key)
        if node is None:
            return None

        if self._is_expired(node):
            # Lazily remove the expired item upon access
            self._remove_node(node)
            del self._cache[key]
            return None

        # Mark as most recently used
        self._move_to_head(node)
        return node.value

    def set(self, key: KT, value: VT) -> None:
        """
        Stores a key-value pair in the cache.

        If the key already exists, its value and expiration time are updated.
        If adding a new entry would exceed the cache's max_size, the
        least-recently-used entry is evicted first.

        Args:
            key: The key of the entry to store.
            value: The value to be associated with the key.
        """
        expires_at = self._now() + self._ttl_seconds

        node = self._cache.get(key)
        if node:
            # Update existing entry
            node.value = value
            node.expires_at = expires_at
            self._move_to_head(node)
        else:
            # Add new entry, evicting LRU if necessary
            if len(self._cache) >= self._max_size:
                lru_node = self._tail.prev
                if lru_node is not self._head:
                    self._remove_node(lru_node)
                    del self._cache[lru_node.key]

            new_node = _Node(key, value, expires_at)
            self._cache[key] = new_node
            self._add_to_head(new_node)
