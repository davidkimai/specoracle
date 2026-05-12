import time
import threading
from dataclasses import dataclass
from typing import Any, Callable, List, Optional


@dataclass
class _IdleConnection:
    connection: Any
    idle_since: float


class ConnectionPool:
    """
    A small idle-connection pool.

    Connections are created by calling the supplied factory. Released connections
    are retained for reuse up to max_size idle connections. Connections that
    cannot be retained, or that are evicted, are closed if they provide a
    callable close() method.
    """

    def __init__(self, factory: Callable[[], Any], *, max_size: int, now: Optional[Callable[[], float]] = None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if isinstance(max_size, bool) or not isinstance(max_size, int):
            raise TypeError("max_size must be an integer")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self._factory = factory
        self._max_size = max_size
        self._now = now if now is not None else time.monotonic
        self._idle: List[_IdleConnection] = []
        self._idle_ids = set()
        self._lock = threading.RLock()

    def acquire(self) -> Any:
        """
        Return an idle connection if available; otherwise create and return a new
        connection using the factory.
        """
        with self._lock:
            if self._idle:
                item = self._idle.pop()
                self._idle_ids.discard(id(item.connection))
                return item.connection

        return self._factory()

    def release(self, conn: Any) -> None:
        """
        Return conn to the idle pool if there is idle capacity. If the idle pool
        is already full, close conn if possible.
        """
        should_close = False

        with self._lock:
            conn_id = id(conn)
            if conn_id in self._idle_ids:
                raise ValueError("connection is already idle in this pool")

            if len(self._idle) < self._max_size:
                self._idle.append(_IdleConnection(conn, self._current_time()))
                self._idle_ids.add(conn_id)
            else:
                should_close = True

        if should_close:
            self._close_connection(conn)

    def evict_idle(self, max_idle_seconds: float) -> int:
        """
        Close and remove idle connections that have been idle for more than
        max_idle_seconds. Returns the number of evicted connections.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be non-negative")

        cutoff_now = self._current_time()
        kept: List[_IdleConnection] = []
        evicted: List[Any] = []

        with self._lock:
            for item in self._idle:
                if cutoff_now - item.idle_since > max_idle_seconds:
                    evicted.append(item.connection)
                    self._idle_ids.discard(id(item.connection))
                else:
                    kept.append(item)
            self._idle = kept

        self._close_many(evicted)
        return len(evicted)

    def _current_time(self) -> float:
        return float(self._now())

    @staticmethod
    def _close_connection(conn: Any) -> None:
        close = getattr(conn, "close", None)
        if callable(close):
            close()

    @classmethod
    def _close_many(cls, connections: List[Any]) -> None:
        first_exception = None

        for conn in connections:
            try:
                cls._close_connection(conn)
            except Exception as exc:  # noqa: BLE001 - preserve close behavior while closing all
                if first_exception is None:
                    first_exception = exc

        if first_exception is not None:
            raise first_exception
