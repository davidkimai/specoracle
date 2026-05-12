# -*- coding: utf-8 -*-
"""
A thread-safe connection pool implementation.
"""

import collections
import threading
import time
import typing

# Define a protocol for connection objects that the pool can manage.
# They must have a `close()` method.
class Closable(typing.Protocol):
    """A protocol for objects with a close() method."""

    def close(self) -> None:
        """Closes the resource."""
        ...


C = typing.TypeVar("C", bound=Closable)


class ConnectionPoolError(Exception):
    """Base exception for connection pool errors."""
    pass


class ConnectionPoolFullError(ConnectionPoolError):
    """Raised when trying to acquire a connection from a full pool."""
    pass


class ConnectionNotFromPoolError(ConnectionPoolError):
    """Raised when trying to release a connection not managed by the pool."""
    pass


def _validate_constructor_args(
    factory: typing.Callable[[], C], max_size: int
) -> None:
    """Validate arguments for the ConnectionPool constructor."""
    if not callable(factory):
        raise TypeError("factory must be a callable")
    if not isinstance(max_size, int) or max_size <= 0:
        raise ValueError("max_size must be a positive integer")


class ConnectionPool(typing.Generic[C]):
    """
    A thread-safe, generic connection pool.

    The pool manages a collection of connection objects created by a provided
    factory. It limits the total number of connections (both active and idle)
    to a specified maximum size.
    """

    def __init__(
        self,
        factory: typing.Callable[[], C],
        *,
        max_size: int,
        now: typing.Optional[typing.Callable[[], float]] = None,
    ):
        """
        Initializes a new ConnectionPool.

        Args:
            factory: A zero-argument callable that returns a new connection
                object. The connection object must have a `close()` method.
            max_size: The maximum number of connections allowed in the pool.
            now: An optional callable that returns the current time as a float.
                Used for testing. Defaults to `time.monotonic`.
        """
        _validate_constructor_args(factory, max_size)

        self._factory = factory
        self._max_size = max_size
        self._now = now or time.monotonic

        self._lock = threading.Lock()
        self._idle_connections: collections.deque[tuple[C, float]] = collections.deque()
        self._active_connections: set[C] = set()

    @property
    def size(self) -> int:
        """The total number of connections (active and idle) in the pool."""
        with self._lock:
            return len(self._active_connections) + len(self._idle_connections)

    @property
    def active_size(self) -> int:
        """The number of connections currently in use."""
        with self._lock:
            return len(self._active_connections)

    @property
    def idle_size(self) -> int:
        """The number of idle connections available in the pool."""
        with self._lock:
            return len(self._idle_connections)

    def acquire(self) -> C:
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
            if self._idle_connections:
                conn, _ = self._idle_connections.popleft()
                self._active_connections.add(conn)
                return conn

            if self.size < self._max_size:
                conn = self._factory()
                self._active_connections.add(conn)
                return conn

            raise ConnectionPoolFullError(
                f"Connection pool is full (max_size={self._max_size})"
            )

    def release(self, conn: C) -> None:
        """
        Returns a connection to the pool, marking it as idle.

        Args:
            conn: The connection object to release.

        Raises:
            ConnectionNotFromPoolError: If the connection does not belong to
                this pool's set of active connections.
        """
        with self._lock:
            if conn not in self._active_connections:
                raise ConnectionNotFromPoolError(
                    "Cannot release a connection that was not acquired from this pool."
                )

            self._active_connections.remove(conn)
            self._idle_connections.append((conn, self._now()))

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Closes and removes idle connections older than a threshold.

        This method iterates through the idle connections and closes any that
        have been idle for longer than `max_idle_seconds`. The connection's
        `close()` method is called outside the pool's lock to avoid holding
        it during potentially blocking I/O operations.

        Args:
            max_idle_seconds: The maximum time in seconds a connection can
                remain idle before being evicted.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds cannot be negative")

        connections_to_close: list[C] = []
        with self._lock:
            current_time = self._now()
            while self._idle_connections:
                # Peek at the oldest connection without removing it.
                conn, idle_since = self._idle_connections[0]
                idle_duration = current_time - idle_since

                if idle_duration > max_idle_seconds:
                    # Remove from the deque and schedule for closing.
                    self._idle_connections.popleft()
                    connections_to_close.append(conn)
                else:
                    # Since connections are ordered by idle time, we can stop.
                    break

        # Close connections outside the lock.
        for conn in connections_to_close:
            try:
                conn.close()
            except Exception:
                # Intentionally suppress exceptions during close, as the
                # connection is being discarded anyway.
                pass
