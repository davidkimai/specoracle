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
        Maximum number of idle connections kept in the pool.
    now : callable, optional
        Zero-argument callable that returns the current time as a float
        (seconds).  Defaults to ``time.monotonic``.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if max_size < 0:
            raise ValueError("max_size must be >= 0")
        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        # Each entry in the deque is (connection, idle_since)
        self._idle: deque = deque()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection from the pool, or create a new one.

        If there are idle connections available the most recently returned
        one is handed out (LIFO, to keep the "hot" connection in use and
        let stale ones time out naturally).

        Returns
        -------
        connection
            A connection object produced by *factory*.
        """
        with self._lock:
            if self._idle:
                conn, _idle_since = self._idle.pop()
                return conn
        # No idle connection available – create a fresh one outside the lock
        # so that a slow factory does not block other threads unnecessarily.
        return self._factory()

    def release(self, conn):
        """
        Return *conn* to the idle pool.

        If the pool is already at *max_size* capacity the connection is
        closed immediately and discarded.

        Parameters
        ----------
        conn
            A connection previously obtained via :meth:`acquire`.
        """
        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((conn, self._now()))
                return
        # Pool is full – close the connection outside the lock.
        self._close(conn)

    def evict_idle(self, max_idle_seconds: float):
        """
        Close and remove idle connections that have been idle for longer
        than *max_idle_seconds*.

        Parameters
        ----------
        max_idle_seconds : float
            Connections idle for more than this many seconds are evicted.
        """
        cutoff = self._now() - max_idle_seconds
        to_close = []

        with self._lock:
            # Build a new deque keeping only connections that are fresh enough.
            fresh = deque()
            for conn, idle_since in self._idle:
                if idle_since < cutoff:
                    to_close.append(conn)
                else:
                    fresh.append((conn, idle_since))
            self._idle = fresh

        for conn in to_close:
            self._close(conn)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _close(conn):
        """Close a connection, silently ignoring any errors."""
        try:
            conn.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Informational properties (useful for monitoring / testing)
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Number of connections currently sitting idle in the pool."""
        with self._lock:
            return len(self._idle)

    @property
    def max_size(self) -> int:
        """Maximum number of idle connections the pool will retain."""
        return self._max_size

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ConnectionPool idle={self.idle_count}/{self._max_size}>"
        )
