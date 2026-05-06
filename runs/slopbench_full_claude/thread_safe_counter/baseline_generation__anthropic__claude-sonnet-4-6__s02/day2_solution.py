"""
thread_safe_counter.py

Provides BoundedCounter: a thread-safe, named counter with a maximum total.
"""

import threading


class BoundedCounter:
    """Coordinate named integer counters across threads with a global cap."""

    def __init__(self, max_total: int) -> None:
        if max_total <= 0:
            raise ValueError(f"max_total must be positive, got {max_total!r}")
        self._max_total: int = max_total
        self._counters: dict[str, int] = {}
        self._total: int = 0
        self._lock: threading.Lock = threading.Lock()

    def increment(self, name: str) -> int:
        """Increment the named counter by one and return its new value.

        Raises OverflowError if incrementing would exceed max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment '{name}': total would exceed max_total "
                    f"({self._max_total})"
                )
            new_value = self._counters.get(name, 0) + 1
            self._counters[name] = new_value
            self._total += 1
            return new_value

    def decrement(self, name: str) -> int:
        """Decrement the named counter by one and return its new value.

        Raises KeyError if the name is absent or its current value is zero.
        Counts that reach zero are removed from the internal store and will
        not appear in snapshot().
        """
        with self._lock:
            current = self._counters.get(name, 0)
            if current == 0:
                raise KeyError(name)
            new_value = current - 1
            if new_value == 0:
                del self._counters[name]
            else:
                self._counters[name] = new_value
            self._total -= 1
            return new_value

    def total(self) -> int:
        """Return the total count across all named counters."""
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        """Return a copy of all nonzero counts keyed by name."""
        with self._lock:
            return {name: count for name, count in self._counters.items() if count != 0}
