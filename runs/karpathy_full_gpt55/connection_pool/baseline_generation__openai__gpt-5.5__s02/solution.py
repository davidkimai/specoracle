import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Deque, Optional


@dataclass
class _IdleEntry:
    connection: Any
    since: float


class ConnectionPool:
    """
    A small identity-based connection pool.

    Connections are created by the supplied factory when no idle connection is
    available. Released connections are kept idle up to max_size; extra released
    connections are closed instead.

    The pool is thread-safe for acquire, release, evict_idle, and close.
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

        self._lock = threading.RLock()
        self._idle: Deque[_IdleEntry] = deque()
        self._idle_ids: set[int] = set()
        self._in_use_ids: set[int] = set()
        self._closed = False

    def acquire(self) -> Any:
        """
        Return an idle connection if available, otherwise create a new one.

        Raises RuntimeError if the pool has been closed.
        """
        with self._lock:
            self._ensure_open()

            while self._idle:
                entry = self._idle.pop()
                conn_id = id(entry.connection)
                if conn_id in self._idle_ids:
                    self._idle_ids.remove(conn_id)
                    self._in_use_ids.add(conn_id)
                    return entry.connection

        connection = self._factory()
        conn_id = id(connection)

        with self._lock:
            self._ensure_open()
            if conn_id in self._idle_ids or conn_id in self._in_use_ids:
                self._close_connection(connection)
                raise RuntimeError("factory returned a connection already managed by this pool")
            self._in_use_ids.add(conn_id)

        return connection

    def release(self, conn: Any) -> None:
        """
        Return a previously acquired connection to the idle pool.

        If the idle pool is already at capacity, the connection is closed
        instead of being retained.
        """
        conn_id = id(conn)
        should_close = False
        timestamp = self._now()

        with self._lock:
            if conn_id not in self._in_use_ids:
                raise ValueError("connection was not acquired from this pool or was already released")

            self._in_use_ids.remove(conn_id)

            if not self._closed and len(self._idle) < self._max_size:
                self._idle.append(_IdleEntry(conn, float(timestamp)))
                self._idle_ids.add(conn_id)
            else:
                should_close = True

        if should_close:
            self._close_connection(conn)

    def evict_idle(self, max_idle_seconds: float) -> None:
        """
        Close and remove idle connections whose idle time is at least
        max_idle_seconds.
        """
        if max_idle_seconds < 0:
            raise ValueError("max_idle_seconds must be non-negative")

        current_time = float(self._now())
        threshold = float(max_idle_seconds)
        to_close = []

        with self._lock:
            retained: Deque[_IdleEntry] = deque()

            while self._idle:
                entry = self._idle.popleft()
                conn_id = id(entry.connection)

                if conn_id not in self._idle_ids:
                    continue

                if current_time - entry.since >= threshold:
                    self._idle_ids.remove(conn_id)
                    to_close.append(entry.connection)
                else:
                    retained.append(entry)

            self._idle = retained

        self._close_many(to_close)

    def close(self) -> None:
        """
        Close all idle connections and prevent further acquisition.

        Checked-out connections are not forcibly closed by this method; when
        released later, they will be closed instead of being returned to the pool.
        """
        to_close = []

        with self._lock:
            if self._closed:
                return

            self._closed = True

            while self._idle:
                entry = self._idle.popleft()
                conn_id = id(entry.connection)
                if conn_id in self._idle_ids:
                    self._idle_ids.remove(conn_id)
                    to_close.append(entry.connection)

        self._close_many(to_close)

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def idle_count(self) -> int:
        with self._lock:
            return len(self._idle_ids)

    @property
    def in_use_count(self) -> int:
        with self._lock:
            return len(self._in_use_ids)

    @property
    def closed(self) -> bool:
        with self._lock:
            return self._closed

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("connection pool is closed")

    @staticmethod
    def _close_connection(conn: Any) -> None:
        close = getattr(conn, "close", None)
        if callable(close):
            close()

    @classmethod
    def _close_many(cls, connections: list[Any]) -> None:
        first_error = None

        for conn in connections:
            try:
                cls._close_connection(conn)
            except Exception as exc:
                if first_error is None:
                    first_error = exc

        if first_error is not None:
            raise first_error
