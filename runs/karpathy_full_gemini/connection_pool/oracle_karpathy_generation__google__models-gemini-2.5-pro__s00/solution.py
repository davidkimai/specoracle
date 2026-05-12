# -*- coding: utf-8 -*-
"""
A thread-safe generic connection pool implementation.
"""

import collections
import threading
import time
from typing import Callable, Deque, Generic, Optional, Set, Tuple, TypeVar

# A generic type for the connection objects managed by the pool.
T = TypeVar("T")


class ConnectionPoolError(Exception):
    """Base exception for connection pool errors."""


class ConnectionPoolFullError(ConnectionPoolError):
    """Exception raised when the connection pool is full."""


class ConnectionPool(Generic[T]):
    """
    A thread-safe, generic connection pool.

    The pool manages a collection of connections, created by a user-provided
    factory. It supports acquiring connections, releasing them back to the
    pool, and evicting idle connections that have not been used for a
    specified duration.

    The connection objects produced by the factory are expected to have a
    `close()` method for proper resource cleanup during eviction.
    """

    def __init__(
        self,
        factory: Callable[[], T],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a new ConnectionPool.

        Args:
            factory: A callable that takes no arguments and returns a new
                connection object.
            max_size: The maximum number of connections allowed in the pool
                (both active and idle). Must be a positive integer.
            now: An optional callable that returns the current time as a float.
                If None, `time.monotonic` is used. This is useful for testing.

        Raises:
            ValueError: If `max_size` is not a positive integer.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now or time.monotonic

        self._lock = threading.Lock()
        self._idle_connections: Deque[Tuple[T, float]] = collections.deque()
        self._active_connections: Set[T] = set()

    @property
    def max_size(self) -> int:
        """The maximum size of the pool."""
        return self._max_size

    @property
    def size(self) -> int:
        """The current total number of connections (active + idle)."""
        with self._lock:
            return len(self._active_connections) + len(self._idle_connections)

    @property
    def active_size(self) -> int:
        """The current number of active (in-use) connections."""
        with self._lock:
            return len(self._active_connections)

    @property
    def idle_size(self) -> int:
        """The current number of idle (available) connections."""
        with self._lock:
            return len(self._idle_connections)

    def acquire(self) -> T:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned. Otherwise, if the
        pool has not reached its maximum size, a new connection is created
        and returned.

        Returns:
            A connection object from the pool.

        Raises:
            ConnectionPoolFullError: If no idle connections are available and
                the pool is at its maximum size.
        """
        with self._lock:
            # Case 1: Reuse an idle connection.
            if self._idle_connections:
                conn, _ = self._idle_connections.popleft()
                self._active_connections.add(conn)
                return conn

            # Case 2: Create a new connection if capacity allows.
            if self.size < self._max_size:
                conn = self._factory()
                self._active_connections.add(conn)
                return conn

            # Case 3: Pool is full.
            raise ConnectionPoolFullError(
                f"Connection pool is full (max_size={self._max_size})"
            )

    def release(self, conn: T) -> None:
        """
        Releases a connection back to the pool, making it available for reuse.

        The connection is moved from the active set to the idle set.

        Args:
            conn: The connection object to release.

        Raises:
            ValueError: If the connection does not belong to this pool's
                active set.
        """
        with self._lock:
            if conn not in self._active_connections:
                raise ValueError(
                    "The connection being released is not currently active "
                    "in this pool."
                )
            self._active_connections.remove(conn)
            self._idle_connections.append((conn, self._now()))

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Closes and removes idle connections older than a threshold.

        This method iterates through the idle connections, starting with the
        oldest, and closes any connection that has been idle for longer than
        `max_idle_seconds`.

        Args:
            max_idle_seconds: The maximum time in seconds a connection is
                allowed to be idle before being evicted.
        """
        with self._lock:
            now = self._now()
            # Oldest connections are at the left of the deque.
            while self._idle_connections:
                conn, idle_since = self._idle_connections[0]
                if now - idle_since > max_idle_seconds:
                    self._idle_connections.popleft()
                    try:
                        # The factory is expected to produce objects with a
                        # close() method.
                        conn.close()  # type: ignore
                    except Exception:
                        # Ignore errors during close, but continue eviction.
                        pass
                else:
                    # The rest of the connections are newer, so we can stop.
                    break
