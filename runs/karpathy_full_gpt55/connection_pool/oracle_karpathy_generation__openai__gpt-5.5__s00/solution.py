import time


class ConnectionPool:
    def __init__(self, factory, *, max_size: int, now=None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        if isinstance(max_size, bool) or not isinstance(max_size, int):
            raise TypeError("max_size must be an int")
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if now is None:
            now = time.monotonic
        if not callable(now):
            raise TypeError("now must be callable")

        self._factory = factory
        self._max_size = max_size
        self._now = now
        self._idle = []
        self._idle_ids = set()

    def acquire(self):
        if self._idle:
            conn, _ = self._idle.pop()
            self._idle_ids.discard(id(conn))
            return conn
        return self._factory()

    def release(self, conn):
        conn_id = id(conn)
        if conn_id in self._idle_ids:
            return

        if len(self._idle) < self._max_size:
            self._idle.append((conn, self._now()))
            self._idle_ids.add(conn_id)
        else:
            self._close_if_present(conn)

    def evict_idle(self, max_idle_seconds):
        cutoff = self._now() - max_idle_seconds
        kept = []
        evicted = []

        for conn, idle_since in self._idle:
            if idle_since < cutoff:
                evicted.append(conn)
            else:
                kept.append((conn, idle_since))

        self._idle = kept
        self._idle_ids = {id(conn) for conn, _ in kept}

        for conn in evicted:
            self._close_if_present(conn)

    @staticmethod
    def _close_if_present(conn):
        close = getattr(conn, "close", None)
        if callable(close):
            close()
