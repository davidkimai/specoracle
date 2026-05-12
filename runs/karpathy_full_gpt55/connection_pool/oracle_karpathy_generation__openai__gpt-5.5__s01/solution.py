import threading
import time


class ConnectionPool:
    """A small idle-connection pool.

    max_size limits the number of idle connections retained by the pool. acquire()
    creates a new connection when no idle connection is available.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if not isinstance(max_size, int):
            raise TypeError("max_size must be an int")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self._factory = factory
        self._max_size = max_size
        self._now = time.monotonic if now is None else now
        self._idle = []
        self._lock = threading.Lock()

    def acquire(self):
        """Return an idle connection, or create a new one if none is available."""
        with self._lock:
            if self._idle:
                conn, _ = self._idle.pop()
                return conn
        return self._factory()

    def release(self, conn):
        """Return conn to the idle pool if there is capacity; otherwise close it."""
        should_close = False

        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((conn, self._now()))
            else:
                should_close = True

        if should_close:
            conn.close()

    def evict_idle(self, max_idle_seconds):
        """Close and remove idle connections idle for longer than max_idle_seconds."""
        cutoff = self._now() - max_idle_seconds

        with self._lock:
            keep = []
            evict = []
            for conn, idle_since in self._idle:
                if idle_since < cutoff:
                    evict.append(conn)
                else:
                    keep.append((conn, idle_since))
            self._idle = keep

        for conn in evict:
            conn.close()
