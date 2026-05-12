import collections
import contextlib
import threading
import time
from typing import Callable, Deque, Generic, Optional, Set, Tuple, TypeVar

# A generic type for the connection objects managed by the pool.
# This allows for static type checking of the connections.
T_conn = TypeVar("T_conn")


class ConnectionPoolError(Exception):
    """Base exception for connection pool errors."""
    pass


class ConnectionPoolFullError(ConnectionPoolError):
    """Exception raised when trying to acquire a connection from a full pool."""
    pass


class ConnectionPool(Generic[T_conn]):
    """
    A thread-safe, generic connection pool.

    The pool manages a collection of connections, creating them on-demand
    up to a specified maximum size. It supports acquiring, releasing, and
    evicting idle connections.
    """

    def __init__(
        self,
        factory: Callable[[], T_conn],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes the connection pool.

        Args:
            factory: A callable that takes no arguments and returns a new
                connection object. The returned object is expected to have a
                `close()` method.
            max_size: The maximum number of connections (both idle and active)
                that the pool can manage. Must be a positive integer.
            now: An optional callable that returns the current time as a float
                (e.g., `time.time`). This is primarily for testing purposes.
                If None, `time.time` is used.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.time

        self._lock = threading.Lock()

        # Deque of (connection, idle_since_timestamp) for idle connections.
        # LIFO for acquire/release, FIFO for eviction checks.
        self._idle_connections: Deque[Tuple[T_conn, float]] = collections.deque()

        # Set of connections currently in use.
        self._active_connections: Set[T_conn] = set()

    def acquire(self) -> T_conn:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned (LIFO). Otherwise,
        if the pool has not reached its maximum size, a new connection is
        created and returned.

        Returns:
            A connection object from the pool.

        Raises:
            ConnectionPoolFullError: If no idle connections are available and
                the pool is at its maximum size.
        """
        with self._lock:
            # Case 1: Reuse an idle connection.
            if self._idle_connections:
                conn, _ = self._idle_connections.pop()
                self._active_connections.add(conn)
                return conn

            # Case 2: Create a new connection if capacity allows.
            if len(self._idle_connections) + len(self._active_connections) < self._max_size:
                conn = self._factory()
                self._active_connections.add(conn)
                return conn

            # Case 3: Pool is full.
            raise ConnectionPoolFullError(
                f"Connection pool is full (max_size={self._max_size})"
            )

    def release(self, conn: T_conn) -> None:
        """
        Returns a connection to the pool, making it available for reuse.

        The connection is added to the idle pool.

        Args:
            conn: The connection object to release.

        Raises:
            ValueError: If the connection is not active or does not belong to
                this pool.
        """
        with self._lock:
            if conn not in self._active_connections:
                raise ValueError(
                    "Cannot release a connection that is not active or does "
                    "not belong to this pool."
                )

            self._active_connections.remove(conn)
            self._idle_connections.append((conn, self._now()))

    def evict_idle(self, max_idle_seconds: int) -> None:
        """
        Closes and removes idle connections older than a threshold.

        This method iterates through the idle connections (oldest first) and
        closes any that have been idle for longer than `max_idle_seconds`.

        Args:
            max_idle_seconds: The maximum time in seconds a connection can
                remain idle before being a candidate for eviction.
        """
        with self._lock:
            now = self._now()
            # Idle connections are ordered by age, with the oldest at the left.
            # We can iterate from the left and stop when we find a connection
            # that is not stale.
            while self._idle_connections:
                conn, idle_since = self._idle_connections[0]  # Peek at oldest
                if now - idle_since > max_idle_seconds:
                    self._idle_connections.popleft()  # Remove the stale connection
                    try:
                        # Assumes the connection object has a close() method.
                        conn.close()
                    except Exception:
                        # Ignore errors during close, but still evict.
                        pass
                else:
                    # The rest of the connections are newer, so we can stop.
                    break

    @contextlib.contextmanager
    def connection(self):
        """
        A context manager to safely acquire and release a connection.

        This is the recommended way to use the pool, as it ensures that
        connections are always released, even in the case of exceptions.

        Yields:
            A connection object.

        Example:
            pool = ConnectionPool(factory, max_size=10)
            with pool.connection() as conn:
                # use conn
                ...
        """
        conn = None
        try:
            conn = self.acquire()
            yield conn
        finally:
            if conn is not None:
                self.release(conn)
