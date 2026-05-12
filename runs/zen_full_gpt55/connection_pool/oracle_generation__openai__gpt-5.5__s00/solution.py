from dataclasses import dataclass
from numbers import Real
from time import monotonic
from typing import Any, Callable, List, Optional, Set


@dataclass(frozen=True)
class _IdleConnection:
    connection: Any
    idle_since: float


class ConnectionPool:
    def __init__(self, factory: Callable[[], Any], *, max_size: int, now: Optional[Callable[[], float]] = None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if isinstance(max_size, bool) or not isinstance(max_size, int):
            raise TypeError("max_size must be an integer")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable when provided")

        self._factory = factory
        self._max_size = max_size
        self._now = monotonic if now is None else now
        self._idle: List[_IdleConnection] = []
        self._idle_ids: Set[int] = set()

    def acquire(self) -> Any:
        if not self._idle:
            return self._factory()

        idle_connection = self._idle.pop()
        self._idle_ids.remove(idle_connection_id(idle_connection.connection))
        return idle_connection.connection

    def release(self, conn: Any) -> None:
        conn_id = idle_connection_id(conn)
        if conn_id in self._idle_ids:
            raise ValueError("connection is already idle in this pool")

        if len(self._idle) >= self._max_size:
            close_connection(conn)
            return

        self._idle.append(_IdleConnection(conn, self._current_time()))
        self._idle_ids.add(conn_id)

    def evict_idle(self, max_idle_seconds: float) -> int:
        validate_idle_threshold(max_idle_seconds)

        current_time = self._current_time()
        kept: List[_IdleConnection] = []
        evicted = 0

        for idle_connection in self._idle:
            if current_time - idle_connection.idle_since > max_idle_seconds:
                close_connection(idle_connection.connection)
                self._idle_ids.remove(idle_connection_id(idle_connection.connection))
                evicted += 1
            else:
                kept.append(idle_connection)

        self._idle = kept
        return evicted

    def _current_time(self) -> float:
        value = self._now()
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError("now must return a real number")
        return float(value)


def idle_connection_id(conn: Any) -> int:
    return id(conn)


def close_connection(conn: Any) -> None:
    close = getattr(conn, "close", None)
    if not callable(close):
        raise TypeError("connection must have a callable close method")
    close()


def validate_idle_threshold(max_idle_seconds: float) -> None:
    if isinstance(max_idle_seconds, bool) or not isinstance(max_idle_seconds, Real):
        raise TypeError("max_idle_seconds must be a real number")
    if max_idle_seconds < 0:
        raise ValueError("max_idle_seconds must be non-negative")
