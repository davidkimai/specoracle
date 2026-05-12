import math
import time
from dataclasses import dataclass
from numbers import Real
from threading import Lock
from typing import Any, Callable, Optional


__all__ = ["ConnectionPool"]


@dataclass(frozen=True)
class _IdleConnection:
    connection: Any
    returned_at: float


def _require_callable(value: Any, name: str) -> Callable[..., Any]:
    if not callable(value):
        raise TypeError(f"{name} must be callable")
    return value


def _require_non_negative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _require_non_negative_seconds(value: Any, name: str) -> float:
    seconds = _require_finite_real(value, name)
    if seconds < 0:
        raise ValueError(f"{name} must be non-negative")
    return seconds


def _require_finite_real(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a finite real number")

    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be finite") from exc

    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _close_connection(connection: Any) -> None:
    close = getattr(connection, "close", None)
    if not callable(close):
        raise TypeError("connection must provide a callable close() method")
    close()


class ConnectionPool:
    """A small idle-connection pool.

    The pool limits only the number of idle connections it keeps. If the idle
    pool is full when a connection is released, that connection is closed
    instead of being stored.
    """

    def __init__(
        self,
        factory: Callable[[], Any],
        *,
        max_size: int,
        now: Optional[Callable[[], Real]] = None,
    ) -> None:
        self._factory = _require_callable(factory, "factory")
        self._max_size = _require_non_negative_int(max_size, "max_size")
        self._now = time.monotonic if now is None else _require_callable(now, "now")

        self._lock = Lock()
        self._idle: list[_IdleConnection] = []
        self._idle_ids: set[int] = set()

    def acquire(self) -> Any:
        """Return an idle connection, or create a new one if none are idle."""
        with self._lock:
            if self._idle:
                idle = self._idle.pop()
                self._idle_ids.remove(id(idle.connection))
                return idle.connection

        return self._factory()

    def release(self, connection: Any) -> None:
        """Return a connection to the idle pool, or close it if the pool is full."""
        connection_id = id(connection)

        with self._lock:
            if connection_id in self._idle_ids:
                raise ValueError("connection is already idle in this pool")
            has_capacity = len(self._idle) < self._max_size

        if not has_capacity:
            _close_connection(connection)
            return

        returned_at = self._read_time()

        with self._lock:
            if connection_id in self._idle_ids:
                raise ValueError("connection is already idle in this pool")
            if len(self._idle) >= self._max_size:
                should_close = True
            else:
                self._idle.append(_IdleConnection(connection, returned_at))
                self._idle_ids.add(connection_id)
                should_close = False

        if should_close:
            _close_connection(connection)

    def evict_idle(self, max_idle_seconds: Real) -> None:
        """Close and remove idle connections at or beyond the idle threshold."""
        threshold = _require_non_negative_seconds(
            max_idle_seconds,
            "max_idle_seconds",
        )
        current_time = self._read_time()

        with self._lock:
            kept: list[_IdleConnection] = []
            evicted: list[Any] = []

            for idle in self._idle:
                idle_seconds = current_time - idle.returned_at
                if idle_seconds >= threshold:
                    evicted.append(idle.connection)
                    self._idle_ids.remove(id(idle.connection))
                else:
                    kept.append(idle)

            self._idle = kept

        self._close_all(evicted)

    def _read_time(self) -> float:
        return _require_finite_real(self._now(), "now()")

    @staticmethod
    def _close_all(connections: list[Any]) -> None:
        first_error: Optional[Exception] = None
        error_count = 0

        for connection in connections:
            try:
                _close_connection(connection)
            except Exception as exc:
                error_count += 1
                if first_error is None:
                    first_error = exc

        if first_error is not None:
            raise RuntimeError(
                f"failed to close {error_count} evicted connection(s)"
            ) from first_error
