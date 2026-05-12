from collections import deque
from threading import RLock
from time import monotonic


class ConnectionPool:
    """A small idle-connection pool.

    The pool limits the number of idle connections it retains. It does not
    impose a limit on concurrently acquired connections; when no idle
    connection is available, ``factory`` is called to create a new one.
    """

    __slots__ = ("_factory", "_max_size", "_now", "_idle", "_lock")

    def __init__(self, factory, *, max_size: int, now=None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if not isinstance(max_size, int) or isinstance(max_size, bool):
            raise TypeError("max_size must be an integer")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")

        if now is None:
            now = monotonic
        elif not callable(now):
            raise TypeError("now must be callable")

        self._factory = factory
        self._max_size = max_size
        self._now = now
        self._idle = deque()
        self._lock = RLock()

    def acquire(self):
        """Return an idle connection if available, otherwise create one."""
        with self._lock:
            if self._idle:
                _, conn = self._idle.pop()
                return conn

        return self._factory()

    def release(self, conn):
        """Return a connection to the idle pool, or close it if the pool is full."""
        close_conn = False

        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((self._now(), conn))
            else:
                close_conn = True

        if close_conn:
            self._close_connection(conn)

    def evict_idle(self, max_idle_seconds):
        """Close and remove idle connections older than max_idle_seconds."""
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be non-negative")

        to_close = []
        current = self._now()

        with self._lock:
            retained = deque()

            while self._idle:
                released_at, conn = self._idle.popleft()
                if current - released_at > max_idle_seconds:
                    to_close.append(conn)
                else:
                    retained.append((released_at, conn))

            self._idle = retained

        for conn in to_close:
            self._close_connection(conn)

    @staticmethod
    def _close_connection(conn):
        close = getattr(conn, "close", None)
        if close is not None:
            close()
