# connection_pool.py

"""A thread-safe connection pool implementation."""

import collections
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable, Deque, Generic, Iterator, Optional, Set, TypeVar

__all__ = ["ConnectionPool", "PoolError", "PoolFullError"]

# Generic type for the connection object
ConnType = TypeVar("ConnType")


class PoolError(Exception):
    """Base exception for connection pool errors."""
    pass


class PoolFullError(PoolError):
    """Raised when trying to acquire a connection from a full pool."""
    pass


class ConnectionPool(Generic[ConnType]):
    """
    A thread-safe, generic connection pool.

    The pool manages a collection of connections created by a factory. It allows
    callers to acquire connections and release them back to the pool. The pool
    has a maximum size to limit the total number of connections.
    """

    def __init__(
        self,
        factory: Callable[[], ConnType],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a ConnectionPool.

        Args:
            factory: A zero-argument callable that returns a new connection object.
                The connection object is expected to have a `close()` method.
            max_size: The maximum number of connections (both idle and active)
                that the pool can manage. Must be a positive integer.
            now: An optional callable that returns the current time as a float.
                If None, `time.monotonic` is used. This is useful for testing.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now or time.monotonic

        self._lock = threading.Lock()
        self._idle_connections: Deque[tuple[ConnType, float]] = collections.deque()
        self._active_connections: Set[ConnType] = set()

    @property
    def max_size(self) -> int:
        """The maximum number of connections allowed in the pool."""
        return self._max_size

    @property
    def size(self) -> int:
        """The current total number of connections (active + idle)."""
        with self._lock:
            return len(self._active_connections) + len(self._idle_connections)

    @property
    def active_size(self) -> int:
        """The current number of connections in use."""
        with self._lock:
            return len(self._active_connections)

    @property
    def idle_size(self) -> int:
        """The current number of idle connections in the pool."""
        with self._lock:
            return len(self._idle_connections)

    def acquire(self) -> ConnType:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned. Otherwise, if the
        pool is not at its maximum capacity, a new connection is created.

        Returns:
            A connection object.

        Raises:
            PoolFullError: If no idle connections are available and the pool
                has reached its maximum size.
        """
        with self._lock:
            # Case 1: An idle connection is available.
            if self._idle_connections:
                conn, _ = self._idle_connections.popleft()
                self._active_connections.add(conn)
                return conn

            # Case 2: No idle connections, try to create a new one.
            current_size = len(self._active_connections)
            if current_size < self._max_size:
                conn = self._factory()
                self._active_connections.add(conn)
                return conn

            # Case 3: Pool is full.
            raise PoolFullError(
                f"Connection pool is full (max_size={self._max_size})"
            )

    def release(self, conn: ConnType) -> None:
        """
        Returns a connection to the idle pool.

        Args:
            conn: The connection object to release.

        Raises:
            ValueError: If the connection does not belong to this pool's
                active connections.
        """
        with self._lock:
            if conn not in self._active_connections:
                raise ValueError("Cannot release a connection that is not active")

            self._active_connections.remove(conn)
            idle_since = self._now()
            self._idle_connections.append((conn, idle_since))

    @contextmanager
    def connection(self) -> Iterator[ConnType]:
        """
        A context manager to safely acquire and release a connection.

        Yields:
            A connection object.
        """
        conn = None
        try:
            conn = self.acquire()
            yield conn
        finally:
            if conn is not None:
                self.release(conn)

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Closes and removes idle connections older than a specified threshold.

        This method iterates through the idle connections and closes any that
        have been idle for longer than `max_idle_seconds`. It assumes the
        connection objects have a `close()` method.

        Args:
            max_idle_seconds: The maximum time in seconds a connection can
                remain idle before being evicted.
        """
        now = self._now()
        eviction_deadline = now - max_idle_seconds

        to_close = []
        with self._lock:
            while self._idle_connections:
                conn, idle_since = self._idle_connections[0]
                if idle_since < eviction_deadline:
                    self._idle_connections.popleft()
                    to_close.append(conn)
                else:
                    # Idle connections are ordered by time, so we can stop.
                    break

        for conn in to_close:
            try:
                # The connection object is assumed to have a `close` method.
                # In a real-world application, you might want to log failures.
                if hasattr(conn, "close") and callable(getattr(conn, "close")):
                    conn.close()  # type: ignore
            except Exception:
                # Suppress exceptions during close to ensure all evictable
                # connections are processed.
                pass
