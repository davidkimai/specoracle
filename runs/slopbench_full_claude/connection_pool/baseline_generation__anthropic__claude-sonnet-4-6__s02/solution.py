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
        A zero-argument callable that creates and returns a new connection
        object.  The returned object must expose a ``close()`` method.
    max_size : int
        Maximum number of idle connections to keep in the pool.
    now : callable, optional
        A zero-argument callable that returns the current time as a float
        (seconds since epoch).  Defaults to ``time.monotonic``.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if max_size < 0:
            raise ValueError("max_size must be >= 0")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        # Each entry in the deque is a (connection, timestamp) pair where
        # timestamp is the time the connection was placed back into the pool.
        self._idle: deque = deque()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection from the pool, or create a new one.

        Returns
        -------
        connection
            A connection object produced by *factory*.
        """
        with self._lock:
            if self._idle:
                conn, _ts = self._idle.popleft()
                return conn

        # No idle connection available – create a fresh one outside the lock
        # so that a slow factory does not block other threads.
        return self._factory()

    def release(self, conn):
        """
        Return *conn* to the idle pool.

        If the pool is already at *max_size* the connection is closed
        immediately and discarded.

        Parameters
        ----------
        conn : object
            A connection previously obtained via :meth:`acquire`.
        """
        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((conn, self._now()))
                return

        # Pool is full – close the connection outside the lock.
        try:
            conn.close()
        except Exception:
            pass

    def evict_idle(self, max_idle_seconds: float):
        """
        Close and remove idle connections that have been idle for longer
        than *max_idle_seconds*.

        Parameters
        ----------
        max_idle_seconds : float
            Maximum number of seconds a connection may remain idle before
            it is evicted.
        """
        now = self._now()
        to_close = []

        with self._lock:
            # Connections are appended at the right; the oldest ones are at
            # the left.  We drain from the left until we find one that is
            # still within the idle window.
            remaining = deque()
            for conn, ts in self._idle:
                if (now - ts) > max_idle_seconds:
                    to_close.append(conn)
                else:
                    remaining.append((conn, ts))
            self._idle = remaining

        # Close evicted connections outside the lock.
        for conn in to_close:
            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Convenience / introspection
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Return the current number of idle connections in the pool."""
        with self._lock:
            return len(self._idle)

    def __repr__(self) -> str:
        return (
            f"<ConnectionPool max_size={self._max_size} "
            f"idle={self.idle_count}>"
        )
