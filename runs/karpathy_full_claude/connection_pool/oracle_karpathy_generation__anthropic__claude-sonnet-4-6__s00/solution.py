import time
from collections import deque


class ConnectionPool:
    """A simple connection pool with factory, max_size, acquire, release, and evict_idle."""

    def __init__(self, factory, *, max_size: int, now=None):
        # factory: callable that creates a new connection
        # max_size: maximum number of connections (idle + active)
        # now: callable returning current time in seconds (defaults to time.monotonic)
        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        # idle pool: deque of (connection, idle_since) tuples
        self._idle = deque()
        # count of active (acquired but not released) connections
        self._active_count = 0

    def acquire(self):
        """Return an idle connection if available, otherwise create a new one.

        Raises RuntimeError if max_size is reached and no idle connection is available.
        """
        if self._idle:
            conn, _idle_since = self._idle.popleft()
            self._active_count += 1
            return conn

        total = len(self._idle) + self._active_count
        if total >= self._max_size:
            raise RuntimeError("Connection pool exhausted: max_size=%d reached" % self._max_size)

        conn = self._factory()
        self._active_count += 1
        return conn

    def release(self, conn):
        """Return a connection to the idle pool if capacity permits, otherwise close it."""
        self._active_count = max(0, self._active_count - 1)

        total = len(self._idle) + self._active_count
        if total < self._max_size:
            self._idle.append((conn, self._now()))
        else:
            # No room; close the connection if possible
            close = getattr(conn, "close", None)
            if close is not None:
                close()

    def evict_idle(self, max_idle_seconds):
        """Close and remove idle connections that have been idle longer than max_idle_seconds."""
        cutoff = self._now() - max_idle_seconds
        surviving = deque()
        for conn, idle_since in self._idle:
            if idle_since <= cutoff:
                close = getattr(conn, "close", None)
                if close is not None:
                    close()
            else:
                surviving.append((conn, idle_since))
        self._idle = surviving
