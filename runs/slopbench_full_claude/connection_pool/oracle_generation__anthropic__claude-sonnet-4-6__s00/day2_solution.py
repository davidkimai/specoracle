"""
connection_pool.py

A simple, explicit connection pool with idle-eviction support.
"""

import time
from collections import deque


class ConnectionPool:
    """
    A bounded pool of reusable connections.

    Parameters
    ----------
    factory : callable
        Called with no arguments to create a new connection.
        The returned object must have a ``close()`` method.
    max_size : int
        Maximum number of connections the pool will hold.
    now : callable, optional
        Zero-argument callable returning the current time as a float
        (seconds).  Defaults to ``time.monotonic``.  Useful for testing.
    health_check : callable, optional
        Called with a single connection argument before returning an idle
        connection from ``acquire()``.  If it returns ``False`` the
        connection is closed and discarded; the pool then tries the next
        idle connection or creates a new one.  When omitted (or ``None``)
        no health check is performed.
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

        # Each entry: (connection, idle_since)
        self._idle: deque = deque()
        self._total: int = 0  # connections created and not yet closed

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection from the pool, or create a new one.

        When a ``health_check`` is configured, each idle candidate is
        validated before being returned.  Unhealthy connections are closed
        and the search continues.

        Raises
        ------
        RuntimeError
            If the pool is exhausted (all max_size connections are in use
            and none are idle).
        """
        while self._idle:
            conn, _idle_since = self._idle.popleft()

            # Health-check gate (only when a checker is configured)
            if self._health_check is not None:
                try:
                    healthy = self._health_check(conn)
                except Exception:
                    healthy = False

                if not healthy:
                    conn.close()
                    self._total -= 1
                    continue  # try the next idle connection

            return conn

        # No idle connection available — create a fresh one if possible
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

        If the pool is already at capacity (all slots occupied by idle
        connections) the connection is closed and discarded instead.
        """
        if conn is None:
            raise ValueError("Cannot release None")

        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
        else:
            conn.close()
            self._total -= 1

    def evict_idle(self, max_idle_seconds: float) -> int:
        """
        Close and remove idle connections that have been idle longer than
        *max_idle_seconds*.

        Parameters
        ----------
        max_idle_seconds : float
            Age threshold in seconds.

        Returns
        -------
        int
            Number of connections evicted.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be non-negative")

        cutoff = self._now() - max_idle_seconds
        evicted = 0
        survivors: deque = deque()

        for conn, idle_since in self._idle:
            if idle_since < cutoff:
                conn.close()
                self._total -= 1
                evicted += 1
            else:
                survivors.append((conn, idle_since))

        self._idle = survivors
        return evicted

    # ------------------------------------------------------------------
    # Informational helpers
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Number of connections currently sitting idle in the pool."""
        return len(self._idle)

    @property
    def total_count(self) -> int:
        """Total live connections (idle + checked-out)."""
        return self._total

    def __repr__(self) -> str:
        return (
            f"ConnectionPool("
            f"max_size={self._max_size}, "
            f"total={self._total}, "
            f"idle={len(self._idle)})"
        )
