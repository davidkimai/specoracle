import math
import time
from numbers import Real

__all__ = ["ConnectionPool"]


def _validate_max_size(max_size: int) -> int:
    if isinstance(max_size, bool) or not isinstance(max_size, int):
        raise TypeError("max_size must be a non-negative int")
    if max_size < 0:
        raise ValueError("max_size must be a non-negative int")
    return max_size


def _validate_max_idle_seconds(max_idle_seconds: Real) -> Real:
    if isinstance(max_idle_seconds, bool) or not isinstance(max_idle_seconds, Real):
        raise TypeError("max_idle_seconds must be a non-negative real number")
    if not math.isfinite(max_idle_seconds):
        raise ValueError("max_idle_seconds must be finite")
    if max_idle_seconds < 0:
        raise ValueError("max_idle_seconds must be non-negative")
    return max_idle_seconds


def _close_connection(conn) -> None:
    close = getattr(conn, "close", None)
    if not callable(close):
        raise TypeError("connection must provide a callable close() method")
    close()


class ConnectionPool:
    def __init__(self, factory, *, max_size: int, now=None):
        if not callable(factory):
            raise TypeError("factory must be callable")

        clock = time.monotonic if now is None else now
        if not callable(clock):
            raise TypeError("now must be callable")

        self._factory = factory
        self._max_size = _validate_max_size(max_size)
        self._now = clock
        self._idle = []

    def acquire(self):
        if self._idle:
            conn, _idle_since = self._idle.pop()
            return conn
        return self._factory()

    def release(self, conn) -> None:
        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
            return

        _close_connection(conn)

    def evict_idle(self, max_idle_seconds) -> None:
        max_idle_seconds = _validate_max_idle_seconds(max_idle_seconds)
        current_time = self._now()

        retained = []
        evicted = []

        for conn, idle_since in self._idle:
            if current_time - idle_since > max_idle_seconds:
                evicted.append(conn)
            else:
                retained.append((conn, idle_since))

        self._idle = retained

        for conn in evicted:
            _close_connection(conn)
