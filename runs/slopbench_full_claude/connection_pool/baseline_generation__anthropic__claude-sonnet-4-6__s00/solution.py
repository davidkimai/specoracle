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
        A zero-argument callable that creates and returns a new connection.
        The returned connection object is expected to have a ``close()`` method.
    max_size : int
        Maximum number of idle connections to keep in the pool.
    now : callable, optional
        A zero-argument callable returning the current time as a float
        (seconds since epoch).  Defaults to ``time.monotonic``.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if not isinstance(max_size, int) or max_size < 1:
            raise ValueError("max_size must be a positive integer")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        # Each entry in the deque is a (timestamp, connection) tuple where
        # timestamp records when the connection was returned to the idle pool.
        self._idle: deque = deque()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection from the pool, or create a new one.

        If idle connections are available the most-recently-returned one is
        used (LIFO), which tends to keep the working set small and lets
        truly idle connections age out more quickly.

        Returns
        -------
        connection
            A connection object produced by *factory*.
        """
        with self._lock:
            if self._idle:
                _timestamp, conn = self._idle.pop()
                return conn

        # No idle connection available – create a fresh one outside the lock
        # so that a potentially slow factory does not block other threads.
        return self._factory()

    def release(self, conn):
        """
        Return *conn* to the idle pool.

        If the pool is already at capacity the connection is closed
        immediately and discarded.

        Parameters
        ----------
        conn : connection
            A connection previously obtained from :meth:`acquire`.
        """
        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((self._now(), conn))
                return

        # Pool is full – close outside the lock.
        self._close(conn)

    def evict_idle(self, max_idle_seconds: float):
        """
        Close and remove idle connections that have been idle for longer
        than *max_idle_seconds*.

        Parameters
        ----------
        max_idle_seconds : float
            Maximum allowed idle time in seconds.  Connections idle for
            strictly more than this value are evicted.
        """
        cutoff = self._now() - max_idle_seconds
        to_close = []

        with self._lock:
            # Keep only connections that are still fresh enough.
            fresh = deque()
            while self._idle:
                entry = self._idle.popleft()
                timestamp, conn = entry
                if timestamp <= cutoff:
                    to_close.append(conn)
                else:
                    fresh.append(entry)
            self._idle = fresh

        for conn in to_close:
            self._close(conn)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _close(conn):
        """Attempt to close *conn*, ignoring any errors."""
        try:
            conn.close()
        except Exception:
            pass
