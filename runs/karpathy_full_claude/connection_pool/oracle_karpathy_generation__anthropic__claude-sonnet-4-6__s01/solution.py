import time
from collections import deque


class ConnectionPool:
    """
    A simple connection pool.

    Parameters
    ----------
    factory : callable
        Called with no arguments to create a new connection.
        The returned object must have a .close() method.
    max_size : int
        Maximum number of idle connections kept in the pool.
    now : callable, optional
        Zero-argument callable returning the current time as a float
        (seconds).  Defaults to time.monotonic.  Useful for testing.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if max_size < 0:
            raise ValueError("max_size must be >= 0")
        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        # Each entry in the deque is (connection, timestamp_when_returned).
        self._idle: deque = deque()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self):
        """Return an idle connection, or create a new one if none available."""
        while self._idle:
            conn, _ = self._idle.popleft()
            return conn
        return self._factory()

    def release(self, conn) -> None:
        """Return *conn* to the idle pool if capacity permits; close it otherwise."""
        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
        else:
            conn.close()

    def evict_idle(self, max_idle_seconds: float) -> None:
        """Close and remove idle connections that have been idle longer than
        *max_idle_seconds*."""
        cutoff = self._now() - max_idle_seconds
        # Connections were appended in release() order; oldest are at the left.
        # We rebuild the deque keeping only those that are still fresh.
        fresh = deque()
        while self._idle:
            conn, ts = self._idle.popleft()
            if ts >= cutoff:
                fresh.append((conn, ts))
            else:
                conn.close()
        self._idle = fresh
