from __future__ import annotations

import threading


class BoundedCounter:
    """Thread-safe collection of named counters with a shared upper bound."""

    def __init__(self, max_total: int):
        if not isinstance(max_total, int) or isinstance(max_total, bool):
            raise TypeError("max_total must be an integer")
        if max_total <= 0:
            raise ValueError("max_total must be positive")

        self._max_total = max_total
        self._total = 0
        self._counts: dict[str, int] = {}
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """Increment a named counter and return its new value."""
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError("maximum total count exceeded")

            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            self._total += 1
            return new_value

    def total(self) -> int:
        """Return the total count across all names."""
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        """Return a copy of nonzero counts by name."""
        with self._lock:
            return dict(self._counts)
