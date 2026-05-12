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
        object.  The returned connection is expected to have a ``close()``
        method.
    max_size : int
        Maximum number of connections that may exist at one time (both idle
        and active).
    now : callable, optional
        Zero-argument callable that returns the current time as a float
        (seconds).  Defaults to ``time.monotonic``.  Useful for testing.
    """

    def __init__(self, factory, *, max_size: int, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic

        self._lock = threading.Lock()
        # Each entry in the idle deque is a (connection, idle_since) tuple.
        self._idle: deque = deque()
        # Total number of connections currently alive (idle + active).
        self._total: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection from the pool, or create a new one.

        Raises
        ------
        RuntimeError
            If the pool is exhausted (all *max_size* connections are active
            and none are idle).
        """
        with self._lock:
            # Prefer an existing idle connection.
            if self._idle:
                conn, _idle_since = self._idle.popleft()
                return conn

            # Create a new connection if capacity allows.
            if self._total < self._max_size:
                conn = self._factory()
                self._total += 1
                return conn

            raise RuntimeError(
                "Connection pool exhausted: all connections are in use "
                f"(max_size={self._max_size})"
            )

    def release(self, conn):
        """
        Return *conn* to the idle pool.

        If the pool already holds ``max_size`` idle connections the connection
        is closed immediately and discarded.
        """
        with self._lock:
            if len(self._idle) < self._max_size:
                self._idle.append((conn, self._now()))
            else:
                # No room – close and forget.
                try:
                    conn.close()
                finally:
                    self._total -= 1

    def evict_idle(self, max_idle_seconds: float):
        """
        Close and remove idle connections that have been idle for longer than
        *max_idle_seconds*.

        Parameters
        ----------
        max_idle_seconds : float
            Connections idle for more than this many seconds are evicted.
        """
        cutoff = self._now() - max_idle_seconds
        to_close = []

        with self._lock:
            surviving = deque()
            for conn, idle_since in self._idle:
                if idle_since < cutoff:
                    to_close.append(conn)
                    self._total -= 1
                else:
                    surviving.append((conn, idle_since))
            self._idle = surviving

        # Close outside the lock so we don't hold it during potentially slow
        # I/O operations.
        for conn in to_close:
            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Informational helpers (useful for monitoring / testing)
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Number of currently idle connections."""
        with self._lock:
            return len(self._idle)

    @property
    def total_count(self) -> int:
        """Total number of live connections (idle + active)."""
        with self._lock:
            return self._total

    @property
    def active_count(self) -> int:
        """Number of connections currently checked out."""
        with self._lock:
            return self._total - len(self._idle)
