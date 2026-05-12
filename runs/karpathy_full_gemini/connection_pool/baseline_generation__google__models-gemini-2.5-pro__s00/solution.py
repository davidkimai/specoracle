import collections
import contextlib
import threading
import time
from typing import Callable, Deque, Generic, Optional, Set, Tuple, TypeVar

# A generic type for the connection objects managed by the pool.
# It is assumed that connection objects have a `close()` method.
T_conn = TypeVar("T_conn")


class ConnectionPool(Generic[T_conn]):
    """
    A thread-safe, generic connection pool.

    The pool manages a limited number of connections, creating them on demand
    using a provided factory function. It supports acquiring and releasing
    connections, and evicting connections that have been idle for too long.

    Attributes:
        factory: A callable that produces new connection objects.
        max_size: The maximum number of connections (both active and idle)
                  allowed in the pool.
    """

    def __init__(
        self,
        factory: Callable[[], T_conn],
        *,
        max_size: int,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes a new ConnectionPool.

        Args:
            factory: A zero-argument function that returns a new connection object.
                     The returned object is expected to have a `close()` method.
            max_size: The maximum number of connections this pool can manage.
                      Must be a positive integer.
            now: An optional function that returns the current time as a float.
                 Defaults to `time.monotonic`. Used for testing.

        Raises:
            ValueError: If `max_size` is not a positive integer.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer.")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        self._lock = threading.Condition()
        self._idle_connections: Deque[Tuple[T_conn, float]] = collections.deque()
        self._active_connections: Set[T_conn] = set()

    @property
    def size(self) -> int:
        """The total number of connections (idle + active) currently managed."""
        with self._lock:
            return len(self._idle_connections) + len(self._active_connections)

    @property
    def idle_size(self) -> int:
        """The number of idle connections currently in the pool."""
        with self._lock:
            return len(self._idle_connections)

    @property
    def active_size(self) -> int:
        """The number of connections currently checked out from the pool."""
        with self._lock:
            return len(self._active_connections)

    def acquire(self) -> T_conn:
        """
        Acquires a connection from the pool.

        If an idle connection is available, it is returned immediately.
        If no idle connections are available and the pool has not reached its
        maximum size, a new connection is created and returned.
        If the pool is full (all connections are active), this method blocks
        until another thread releases a connection.

        Returns:
            A connection object from the pool.
        """
        with self._lock:
            while True:
                # Case 1: An idle connection is available.
                if self._idle_connections:
                    conn, _ = self._idle_connections.popleft()
                    self._active_connections.add(conn)
                    return conn

                # Case 2: Pool is not full, so create a new connection.
                if self.size < self._max_size:
                    try:
                        conn = self._factory()
                    except Exception:
                        # If the factory fails, we should notify any waiting
                        # threads so they don't wait forever.
                        self._lock.notify_all()
                        raise
                    self._active_connections.add(conn)
                    return conn

                # Case 3: Pool is full, wait for a connection to be released.
                self._lock.wait()

    def release(self, conn: T_conn) -> None:
        """
        Returns a connection to the pool, making it available for other threads.

        Args:
            conn: The connection object that was previously acquired.

        Raises:
            ValueError: If the connection does not belong to this pool's
                        active connections.
        """
        with self._lock:
            if conn not in self._active_connections:
                raise ValueError(
                    "Cannot release a connection that is not active in this pool."
                )

            self._active_connections.remove(conn)
            self._idle_connections.append((conn, self._now()))
            # Notify one waiting thread that a connection is now available.
            self._lock.notify()

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Closes and removes any idle connection that has been idle for too long.

        This method iterates through the idle connections and closes any that
        have been idle for more than `max_idle_seconds`.

        Args:
            max_idle_seconds: The maximum time in seconds a connection is
                              allowed to be idle.

        Raises:
            ValueError: If `max_idle_seconds` is negative.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be non-negative.")

        with self._lock:
            current_time = self._now()
            # Iterate from the oldest connections (left of the deque).
            while self._idle_connections:
                conn, idle_since = self._idle_connections[0]
                if current_time - idle_since > max_idle_seconds:
                    self._idle_connections.popleft()
                    try:
                        # The user-provided connection object is expected to have
                        # a `close()` method.
                        conn.close()
                    except Exception:
                        # In a real application, this failure should be logged.
                        pass
                else:
                    # Since connections are ordered by idle time, we can stop.
                    break

    @contextlib.contextmanager
    def connection(self):
        """
        A context manager to safely acquire and release a connection.

        Yields:
            A connection object from the pool.
        """
        conn = None
        try:
            conn = self.acquire()
            yield conn
        finally:
            if conn is not None:
                self.release(conn)
