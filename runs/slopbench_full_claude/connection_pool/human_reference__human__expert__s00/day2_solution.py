from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class ConnectionPool:
    def __init__(
        self,
        factory: Callable[[], Any],
        *,
        max_size: int,
        now: Callable[[], float] | None = None,
        health_check: Callable[[Any], bool] | None = None,
    ) -> None:
        if max_size <= 0:
            raise ValueError('max_size must be positive')
        self._factory = factory
        self._max_size = max_size
        self._now = now or time.monotonic
        self._health_check = health_check
        self._idle: list[tuple[Any, float]] = []

    def acquire(self):
        while self._idle:
            conn, _stamp = self._idle.pop()
            if self._health_check is None or self._health_check(conn):
                return conn
            if hasattr(conn, 'close'):
                conn.close()
        return self._factory()

    def release(self, conn) -> None:
        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
        elif hasattr(conn, 'close'):
            conn.close()

    def evict_idle(self, max_idle_seconds: float) -> None:
        kept = []
        current = self._now()
        for conn, stamp in self._idle:
            if current - stamp > max_idle_seconds:
                if hasattr(conn, 'close'):
                    conn.close()
            else:
                kept.append((conn, stamp))
        self._idle = kept
