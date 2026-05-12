"""
connection_pool.py

A simple connection pool implementation.
"""

import time
import threading
from collections import deque


class ConnectionPool:
    """
    A thread-safe connection pool.

    Parameters
    ----------
    factory : callable
        Called with no arguments to create a new connection.
        The returned connection object should have a ``close()`` method.
    max_size : int
        Maximum number of connections the pool will hold in the idle queue.
    now : callable, optional
        Zero-argument callable that returns the current time as a float
        (seconds).  Defaults to ``time.monotonic``.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        # Each entry in the deque is a (connection, timestamp) tuple where
        # timestamp records when the connection was returned to the pool.
        self._idle: deque = deque()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection from the pool, or create a new one.

        If there are idle connections available the most recently returned
        one is handed out (LIFO order, which tends to keep connections warm).
        Otherwise a fresh connection is created via the factory.

        Returns
        -------
        connection
            A connection object produced by the factory.
        """
        with self._lock:
            if self._idle:
                conn, _ts = self._idle.pop()
                return conn
        # No idle connection available – create a new one outside the lock
        # so that slow factory calls do not block other threads.
        return self._factory()

    def release(self, conn):
        """
        Return *conn* to the idle pool.

        If the pool is already at capacity the connection is closed and
        discarded rather than queued.

        Parameters
        ----------
        conn :
            A connection previously obtained from :meth:`acquire`.
        """
        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((conn, self._now()))
                return
        # Pool is full – close the surplus connection outside the lock.
        try:
            conn.close()
        except Exception:
            pass

    def evict_idle(self, max_idle_seconds: float):
        """
        Close and remove connections that have been idle for too long.

        Parameters
        ----------
        max_idle_seconds : float
            Connections that have been sitting in the pool for longer than
            this many seconds are evicted.
        """
        cutoff = self._now() - max_idle_seconds
        to_close = []

        with self._lock:
            # Rebuild the deque keeping only connections that are still fresh.
            fresh = deque()
            for conn, ts in self._idle:
                if ts >= cutoff:
                    fresh.append((conn, ts))
                else:
                    to_close.append(conn)
            self._idle = fresh

        # Close stale connections outside the lock.
        for conn in to_close:
            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Number of connections currently sitting in the idle pool."""
        with self._lock:
            return len(self._idle)

    def close_all(self):
        """Close every idle connection and empty the pool."""
        with self._lock:
            to_close = list(self._idle)
            self._idle.clear()

        for conn, _ts in to_close:
            try:
                conn.close()
            except Exception:
                pass

    def __repr__(self) -> str:
        return (
            f"ConnectionPool("
            f"max_size={self._max_size}, "
            f"idle={self.idle_count})"
        )
