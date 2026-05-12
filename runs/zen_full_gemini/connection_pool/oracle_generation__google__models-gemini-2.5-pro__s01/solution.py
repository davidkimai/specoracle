"""
A thread-unsafe connection pool implementation.
"""

import collections
import contextlib
import time
from typing import Any, Callable, Deque, Generator, Optional, Set, Tuple


class PoolError(Exception):
    """Base exception for connection pool errors."""
    pass


class PoolFullError(PoolError):
    """Exception raised when the connection pool is full."""
    pass


class ConnectionPool:
    """
    A generic, thread-unsafe connection pool.

    This pool manages a collection of connection objects created by a factory.
    It supports acquiring, releasing, and evicting idle connections.
    """

    def __init__(
        self,
        factory: Callable[[], Any],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a new connection pool.

        Args:
            factory: A zero-argument callable that returns a new connection object.
                The returned object must have a `close()` method.
            max_size: The maximum number of connections (both active and idle)
                that the pool can manage.
            now: An optional callable that returns the current time as a float.
                If None, defaults to `time.monotonic`. This is primarily for
                testing purposes.

        Raises:
            ValueError: If `max_size` is not a positive integer.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        self._idle_connections: Deque[Tuple[Any, float]] = collections.deque()
        self._active_connections: Set[Any] = set()

    @property
    def size(self) -> int:
        """The total number of connections in the pool (active + idle)."""
        return len(self._active_connections) + len(self._idle_connections)

    def acquire(self) -> Any:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned. Otherwise, if the
        pool has not reached its maximum size, a new connection is created
        and returned.

        Returns:
            A connection object from the pool.

        Raises:
            PoolFullError: If no idle connections are available and the pool
                is at its maximum size.
        """
        if self._idle_connections:
            connection, _ = self._idle_connections.popleft()
            self._active_connections.add(connection)
            return connection

        if self.size < self._max_size:
            connection = self._factory()
            self._active_connections.add(connection)
            return connection

        raise PoolFullError(f"Pool is full with {self.size} connections")

    def release(self, connection: Any) -> None:
        """
        Returns a connection to the idle pool.

        The connection is marked as idle and will be available for future
        `acquire` calls.

        Args:
            connection: The connection object to release.

        Raises:
            ValueError: If the connection does not belong to this pool's
                set of active connections.
        """
        if connection not in self._active_connections:
            raise ValueError(
                "Cannot release a connection that is not active in this pool"
            )

        self._active_connections.remove(connection)
        self._idle_connections.append((connection, self._now()))

    def evict_idle(self, max_idle_seconds: float) -> int:
        """
        Closes and removes idle connections older than a time threshold.

        Args:
            max_idle_seconds: The maximum time in seconds a connection is
                allowed to be idle before being closed and removed.

        Returns:
            The number of connections that were evicted.

        Raises:
            ValueError: If `max_idle_seconds` is negative.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds cannot be negative")

        eviction_threshold = self._now() - max_idle_seconds
        eviction_count = 0

        while self._idle_connections:
            # Peek at the oldest idle connection (left of the deque).
            _connection, idle_since = self._idle_connections[0]
            if idle_since < eviction_threshold:
                connection, _ = self._idle_connections.popleft()
                self._close_connection(connection)
                eviction_count += 1
            else:
                # All remaining connections are newer than the threshold.
                break

        return eviction_count

    def _close_connection(self, connection: Any) -> None:
        """Helper to close a single connection, suppressing exceptions."""
        try:
            connection.close()
        except Exception:
            # Errors on close are explicitly silenced for cleanup robustness.
            # In a real application, this might be a good place for logging.
            pass

    def close_all(self) -> None:
        """Closes all connections in the pool (both active and idle)."""
        all_connections = list(self._active_connections) + [
            conn for conn, _ in self._idle_connections
        ]
        self._active_connections.clear()
        self._idle_connections.clear()

        for connection in all_connections:
            self._close_connection(connection)

    @contextlib.contextmanager
    def connection(self) -> Generator[Any, None, None]:
        """
        A context manager for safely acquiring and releasing a connection.

        Yields:
            A connection object that is automatically released upon exiting
            the context.
        """
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)

    def __enter__(self) -> "ConnectionPool":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close_all()
