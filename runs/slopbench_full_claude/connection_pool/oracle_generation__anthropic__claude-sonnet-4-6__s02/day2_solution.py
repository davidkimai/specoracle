"""
connection_pool.py

A simple, explicit connection pool with idle-eviction support.
"""

import time
from collections import deque


class ConnectionPool:
    """
    A bounded connection pool.

    Parameters
    ----------
    factory : callable
        Called with no arguments to create a new connection.  The returned
        object must expose a ``close()`` method.
    max_size : int
        Maximum number of connections that may exist at one time (idle + in-use).
    now : callable, optional
        Zero-argument callable returning the current time as a float (seconds).
        Defaults to ``time.monotonic``.  Useful for testing.
    health_check : callable, optional
        Called with a single connection argument before returning an idle
        connection from ``acquire()``.  If it returns ``False`` the connection
        is closed and the next idle connection is tried (or a new one is
        created).  When omitted (or ``None``) all idle connections are assumed
        healthy.
    """

    def __init__(self, factory, *, max_size: int, now=None, health_check=None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if not isinstance(max_size, int) or max_size < 1:
            raise ValueError("max_size must be a positive integer")
        if health_check is not None and not callable(health_check):
            raise TypeError("health_check must be callable or None")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        self._health_check = health_check

        # Each entry: (connection, idle_since_timestamp)
        self._idle: deque = deque()
        # Total connections alive (idle + checked-out)
        self._total: int = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection if one is available, otherwise create a new
        one.  Raises ``RuntimeError`` when the pool is exhausted.

        If a ``health_check`` was provided, each idle candidate is validated
        before being returned.  Unhealthy connections are closed and the next
        candidate is tried.
        """
        while self._idle:
            conn, _idle_since = self._idle.popleft()
            if self._health_check is not None and not self._health_check(conn):
                self._close(conn)
                continue
            return conn

        if self._total >= self._max_size:
            raise RuntimeError(
                f"Connection pool exhausted (max_size={self._max_size})"
            )

        conn = self._factory()
        self._total += 1
        return conn

    def release(self, conn) -> None:
        """
        Return *conn* to the idle pool.

        If the pool is already at capacity (all slots filled by idle
        connections), the connection is closed and discarded instead.
        """
        if conn is None:
            raise ValueError("conn must not be None")

        if len(self._idle) >= self._max_size:
            # Pool is full; discard rather than overflow.
            self._close(conn)
            return

        self._idle.append((conn, self._now()))

    def evict_idle(self, max_idle_seconds: float) -> int:
        """
        Close and remove idle connections that have been idle longer than
        *max_idle_seconds*.

        Returns the number of connections evicted.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be non-negative")

        cutoff = self._now() - max_idle_seconds
        survivors: deque = deque()
        evicted = 0

        for conn, idle_since in self._idle:
            if idle_since < cutoff:
                self._close(conn)
                evicted += 1
            else:
                survivors.append((conn, idle_since))

        self._idle = survivors
        return evicted

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _close(self, conn) -> None:
        """Close *conn* and decrement the live-connection counter."""
        conn.close()
        self._total -= 1

    # ------------------------------------------------------------------
    # Informational properties
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Number of connections currently idle in the pool."""
        return len(self._idle)

    @property
    def total_count(self) -> int:
        """Total number of live connections (idle + checked-out)."""
        return self._total
