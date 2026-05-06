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
        Called with no arguments to create a new connection.
        The returned object must have a ``close()`` method.
    max_size : int
        Maximum number of connections that may exist at once.
    now : callable, optional
        Zero-argument callable returning the current time as a float
        (seconds).  Defaults to ``time.monotonic``.  Primarily useful
        for testing.
    health_check : callable, optional
        Called with a single connection as its argument.  Should return
        ``True`` if the connection is still usable, ``False`` otherwise.
        When ``False`` is returned the connection is closed and the pool
        continues looking for a healthy idle connection or creates a new
        one.  When omitted (or ``None``) no health checking is performed.
    """

    def __init__(self, factory, *, max_size: int, now=None, health_check=None):
        if max_size < 1:
            raise ValueError(f"max_size must be >= 1, got {max_size!r}")
        if not callable(factory):
            raise TypeError(f"factory must be callable, got {factory!r}")
        if health_check is not None and not callable(health_check):
            raise TypeError(
                f"health_check must be callable or None, got {health_check!r}"
            )

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        self._health_check = health_check

        # Each entry: (connection, idle_since)
        self._idle: deque = deque()

        # Total connections currently managed (idle + checked-out).
        self._total = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def acquire(self):
        """
        Return an idle connection, or create a new one if capacity allows.

        When a ``health_check`` is configured, each idle candidate is
        validated before being returned.  Unhealthy connections are closed
        and the search continues.  If all idle connections are unhealthy
        and capacity permits, a fresh connection is created.

        Raises
        ------
        RuntimeError
            If the pool is at capacity and no idle connection is available.
        """
        while self._idle:
            conn, _idle_since = self._idle.popleft()
            if self._health_check is not None:
                try:
                    healthy = self._health_check(conn)
                except Exception:
                    healthy = False
                if not healthy:
                    conn.close()
                    self._total -= 1
                    continue
            return conn

        if self._total < self._max_size:
            conn = self._factory()
            self._total += 1
            return conn

        raise RuntimeError(
            f"Connection pool exhausted (max_size={self._max_size}). "
            "No idle connections available."
        )

    def release(self, conn) -> None:
        """
        Return *conn* to the idle pool.

        If the pool already holds ``max_size`` idle connections the
        connection is closed immediately instead of being pooled.

        Parameters
        ----------
        conn :
            A connection previously obtained from :meth:`acquire`.
        """
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
            Maximum allowed idle duration in seconds.  Connections idle
            for strictly more than this value are evicted.

        Returns
        -------
        int
            The number of connections that were evicted.
        """
        if max_idle_seconds < 0:
            raise ValueError(
                f"max_idle_seconds must be >= 0, got {max_idle_seconds!r}"
            )

        cutoff = self._now() - max_idle_seconds
        evicted = 0
        surviving: deque = deque()

        for conn, idle_since in self._idle:
            if idle_since < cutoff:
                conn.close()
                self._total -= 1
                evicted += 1
            else:
                surviving.append((conn, idle_since))

        self._idle = surviving
        return evicted

    # ------------------------------------------------------------------
    # Introspection helpers (read-only properties)
    # ------------------------------------------------------------------

    @property
    def idle_count(self) -> int:
        """Number of connections currently sitting idle in the pool."""
        return len(self._idle)

    @property
    def total_count(self) -> int:
        """Total connections managed by the pool (idle + checked-out)."""
        return self._total

    @property
    def max_size(self) -> int:
        """The maximum pool capacity as supplied at construction time."""
        return self._max_size

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"total={self._total}, "
            f"idle={len(self._idle)}, "
            f"max_size={self._max_size})"
        )
