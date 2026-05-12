import time


class ConnectionPool:
    """A small idle-connection pool.

    Assumptions:
    - max_size is the maximum number of idle connections retained by the pool.
    - acquire() creates a new connection when no idle connection is available.
    - release() closes a connection that cannot be retained because the idle pool
      is already at capacity.
    - Connections are expected to provide a close() method when discarded.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        self._idle = []

    def acquire(self):
        if self._idle:
            conn, _ = self._idle.pop()
            return conn
        return self._factory()

    def release(self, conn):
        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
        else:
            conn.close()

    def evict_idle(self, max_idle_seconds):
        cutoff = self._now() - max_idle_seconds
        kept = []
        for conn, released_at in self._idle:
            if released_at < cutoff:
                conn.close()
            else:
                kept.append((conn, released_at))
        self._idle = kept
        return None
