import collections
import time
from typing import Any, Callable, Deque, Optional, Set, Tuple


class PoolError(Exception):
    """Base exception for ConnectionPool errors."""
    pass


class PoolFullError(PoolError):
    """Exception raised when attempting to acquire a connection from a full pool."""
    pass


class InvalidConnectionError(PoolError):
    """Exception raised when an invalid or unknown connection is released."""
    pass


class ConnectionPool:
    """
    A generic, non-thread-safe connection pool.

    This pool manages a collection of connection objects created by a provided
    factory. It supports acquiring, releasing, and evicting idle connections.
    """

    def __init__(
        self,
        factory: Callable[[], Any],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a ConnectionPool.

        Args:
            factory: A zero-argument callable that returns a new connection object.
                The returned connection object is expected to have a `close()` method.
            max_size: The maximum number of connections allowed in the pool
                (both idle and in-use).
            now: An optional zero-argument callable that returns the current time
                as a float. Defaults to `time.monotonic`. Used for testing.
        """
        if not callable(factory):
            raise TypeError("factory must be a callable")
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        # Idle connections are stored with the timestamp of when they were released.
        self._idle_connections: Deque[Tuple[Any, float]] = collections.deque()
        self._in_use_connections: Set[Any] = set()

    @property
    def _total_connections(self) -> int:
        """The total number of connections currently managed by the pool."""
        return len(self._idle_connections) + len(self._in_use_connections)

    def acquire(self) -> Any:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned.
        Otherwise, if the pool has not reached its maximum size, a new
        connection is created and returned.

        Returns:
            A connection object.

        Raises:
            PoolFullError: If no idle connections are available and the pool
                is at its maximum size.
        """
        if self._idle_connections:
            connection, _ = self._idle_connections.popleft()
            self._in_use_connections.add(connection)
            return connection

        if self._total_connections < self._max_size:
            connection = self._factory()
            self._in_use_connections.add(connection)
            return connection

        raise PoolFullError("Connection pool is full")

    def release(self, conn: Any) -> None:
        """
        Returns a connection to the idle pool.

        Args:
            conn: The connection object to release.

        Raises:
            InvalidConnectionError: If the connection is not recognized as
                belonging to this pool's set of in-use connections.
        """
        if conn not in self._in_use_connections:
            raise InvalidConnectionError(
                "Cannot release a connection that is not in use by this pool"
            )

        self._in_use_connections.remove(conn)
        self._idle_connections.append((conn, self._now()))

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Closes and removes idle connections older than the threshold.

        This method iterates through the idle connections, from oldest to newest,
        and closes any connection that has been idle for longer than
        `max_idle_seconds`.

        Args:
            max_idle_seconds: The maximum time in seconds a connection is
                allowed to be idle before being evicted.
        """
        eviction_time_threshold = self._now()

        # Oldest idle connections are at the left of the deque.
        while self._idle_connections:
            connection, release_time = self._idle_connections[0]
            idle_duration = eviction_time_threshold - release_time

            if idle_duration > max_idle_seconds:
                self._idle_connections.popleft()
                try:
                    # Connection objects are expected to have a close() method.
                    connection.close()
                except Exception:
                    # The connection could already be closed or in a bad state.
                    # We proceed with eviction regardless.
                    pass
            else:
                # The rest of the connections are newer, so we can stop.
                break
