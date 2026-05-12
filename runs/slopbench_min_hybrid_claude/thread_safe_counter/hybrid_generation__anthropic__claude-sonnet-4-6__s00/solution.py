"""
thread_safe_counter.py

Thread-safe bounded counter for coordinating named counters across workers.
"""

import threading
from collections import defaultdict


class BoundedCounter:
    """Coordinate named counters across threads with a shared upper bound."""

    def __init__(self, max_total: int) -> None:
        if max_total <= 0:
            raise ValueError(f"max_total must be positive, got {max_total!r}")
        self._max_total = max_total
        self._counts: dict[str, int] = defaultdict(int)
        self._total = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """Increment the named counter by one and return its new value.

        Raises OverflowError if the operation would exceed max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment '{name}': total would exceed max_total={self._max_total}"
                )
            self._total += 1
            self._counts[name] += 1
            return self._counts[name]

    def total(self) -> int:
        """Return the total count across all names."""
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        """Return a copy of nonzero counts keyed by name."""
        with self._lock:
            return {name: count for name, count in self._counts.items() if count > 0}
