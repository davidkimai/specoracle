from __future__ import annotations

import threading


class BoundedCounter:
    def __init__(self, max_total: int):
        if isinstance(max_total, bool) or not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._counts: dict[str, int] = {}
        self._total = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError("total count would exceed max_total")

            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            self._total += 1
            return new_value

    def total(self) -> int:
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)


__all__ = ["BoundedCounter"]
