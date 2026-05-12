"""
A thread-safe, generic connection pool.

This module provides a ConnectionPool class that manages a collection of
connections created by a factory. It is designed to be thread-safe and
provides mechanisms for acquiring, releasing, and evicting idle connections.
"""

import collections
import threading
import time
from contextlib import contextmanager
from typing import Callable, Deque, Generic, Optional, Set, TypeVar

T_conn = TypeVar("T_conn")


class ConnectionPoolError(Exception):
    """Base exception for connection pool errors."""


class ConnectionPoolFullError(ConnectionPoolError):
    """Raised when acquiring a connection from a full pool."""


class InvalidConnectionError(ConnectionPoolError):
    """Raised when releasing a connection not managed by the pool."""


class ConnectionPool(Generic[T_conn]):
    """
    A thread-safe connection pool.

    This pool manages a collection of connections created by a factory.
    It supports acquiring, releasing, and evicting idle connections.
    """

    def __init__(
        self,
        factory: Callable[[], T_conn],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a ConnectionPool.

        Args:
            factory: A callable that takes no arguments and returns a new
                connection object. The returned object should have a `close()`
                method for resource cleanup.
            max_size: The maximum number of connections the pool can manage
                (both idle and in-use).
            now: An optional callable that returns the current time as a float.
                Defaults to `time.monotonic`. Used for testing.
        """
        if not callable(factory):
            raise TypeError("factory must be a callable")
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        self._lock = threading.Lock()
        self._idle_connections: Deque[tuple[T_conn, float]] = collections.deque()
        self._in_use_connections: Set[T_conn] = set()

    def acquire(self) -> T_conn:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned. Otherwise, if the
        pool has not reached its maximum size, a new connection is created.

        Returns:
            A connection object from the pool.

        Raises:
            ConnectionPoolFullError: If no idle connections are available and
                the pool is at its maximum size.
        """
        with self._lock:
            if self._idle_connections:
                conn, _ = self._idle_connections.popleft()
                self._in_use_connections.add(conn)
                return conn

            current_size = len(self._idle_connections) + len(self._in_use_connections)
            if current_size < self._max_size:
                conn = self._factory()
                self._in_use_connections.add(conn)
                return conn

            raise ConnectionPoolFullError(
                f"Connection pool is full (size={current_size}, max_size={self._max_size})"
            )

    def release(self, conn: T_conn) -> None:
        """
        Returns a connection to the pool, marking it as idle.

        Args:
            conn: The connection object to release.

        Raises:
            InvalidConnectionError: If the connection is not recognized as
                being in use by this pool.
        """
        with self._lock:
            if conn not in self._in_use_connections:
                raise InvalidConnectionError(
                    "Cannot release a connection that is not in use by this pool"
                )

            self._in_use_connections.remove(conn)
            idle_since = self._now()
            self._idle_connections.append((conn, idle_since))

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Closes and removes idle connections older than a threshold.

        This method iterates through idle connections and closes any that have
        been idle for longer than `max_idle_seconds`. It assumes connections
        have a `close()` method.

        Args:
            max_idle_seconds: The maximum time in seconds a connection can
                remain idle before being evicted.
        """
        if not isinstance(max_idle_seconds, (int, float)) or max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be a non-negative number")

        eviction_threshold = self._now() - max_idle_seconds
        to_evict = []

        with self._lock:
            while self._idle_connections:
                conn, idle_since = self._idle_connections[0]
                if idle_since < eviction_threshold:
                    to_evict.append(self._idle_connections.popleft()[0])
                else:
                    # Deque is ordered by time; we can stop checking early.
                    break

        # Close connections outside the lock to avoid holding it during I/O.
        for conn in to_evict:
            try:
                conn.close()
            except Exception:
                # A connection's close() method may fail. We explicitly
                # silence this error because the connection has already been
                # removed from the pool's tracking. Continuing to close
                # other connections is more robust than halting the entire
                # eviction process on a single failure.
                pass

    @contextmanager
    def connection(self):
        """
        A context manager for acquiring and automatically releasing a connection.

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
