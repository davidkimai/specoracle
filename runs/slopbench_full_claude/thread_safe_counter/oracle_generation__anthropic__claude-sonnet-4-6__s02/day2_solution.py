"""
thread_safe_counter.py

A thread-safe bounded counter that tracks named counters with a shared maximum.
"""

import threading


class BoundedCounter:
    """Coordinate named integer counters across threads with a shared total cap."""

    def __init__(self, max_total: int) -> None:
        if max_total <= 0:
            raise ValueError(f"max_total must be positive, got {max_total}")
        self._max_total = max_total
        self._counts: dict[str, int] = {}
        self._total: int = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """Increment the named counter by one and return its new value.

        Raises OverflowError if the total would exceed max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment '{name}': total would exceed max_total={self._max_total}"
                )
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            self._total += 1
            return new_value

    def decrement(self, name: str) -> int:
        """Decrement the named counter by one and return its new value.

        Raises KeyError if the name is absent or its count is already zero.
        Counts that reach zero are removed from the internal mapping.
        """
        with self._lock:
            current = self._counts.get(name, 0)
            if current == 0:
                raise KeyError(name)
            new_value = current - 1
            if new_value == 0:
                del self._counts[name]
            else:
                self._counts[name] = new_value
            self._total -= 1
            return new_value

    def total(self) -> int:
        """Return the total count across all named counters."""
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        """Return a copy of all nonzero counts keyed by name."""
        with self._lock:
            return {name: count for name, count in self._counts.items() if count != 0}
