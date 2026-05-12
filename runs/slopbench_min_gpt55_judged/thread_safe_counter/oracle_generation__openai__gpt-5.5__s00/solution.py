from __future__ import annotations

import threading


__all__ = ["BoundedCounter"]


def _require_positive_int(value: int, parameter_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{parameter_name} must be an integer")
    if value <= 0:
        raise ValueError(f"{parameter_name} must be positive")


def _require_str(value: str, parameter_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{parameter_name} must be a string")


class BoundedCounter:
    """Thread-safe collection of named counters with a shared upper bound."""

    __slots__ = ("_max_total", "_counts", "_total", "_lock")

    def __init__(self, max_total: int) -> None:
        _require_positive_int(max_total, "max_total")
        self._max_total = max_total
        self._counts: dict[str, int] = {}
        self._total = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        _require_str(name, "name")

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
            return {name: count for name, count in self._counts.items() if count != 0}
