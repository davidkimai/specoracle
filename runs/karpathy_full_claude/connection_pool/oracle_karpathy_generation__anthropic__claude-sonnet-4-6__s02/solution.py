import time
from collections import deque


class ConnectionPool:
    """A simple connection pool with idle eviction support."""

    def __init__(self, factory, *, max_size: int, now=None):
        # factory: callable that creates a new connection
        # max_size: maximum number of idle connections to retain
        # now: callable returning current time (defaults to time.monotonic)
        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        # Each entry in _idle is (connection, timestamp_when_returned)
        self._idle = deque()

    def acquire(self):
        """Return an idle connection if available, otherwise create a new one."""
        if self._idle:
            conn, _timestamp = self._idle.popleft()
            return conn
        return self._factory()

    def release(self, conn):
        """Return conn to the idle pool if capacity permits, otherwise close it."""
        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
        else:
            if hasattr(conn, 'close'):
                conn.close()

    def evict_idle(self, max_idle_seconds):
        """Close and remove idle connections older than max_idle_seconds."""
        cutoff = self._now() - max_idle_seconds
        surviving = deque()
        for conn, timestamp in self._idle:
            if timestamp >= cutoff:
                surviving.append((conn, timestamp))
            else:
                if hasattr(conn, 'close'):
                    conn.close()
        self._idle = surviving
