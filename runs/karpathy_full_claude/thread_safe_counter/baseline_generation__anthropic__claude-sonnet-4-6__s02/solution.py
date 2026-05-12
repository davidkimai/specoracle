"""
thread_safe_counter.py

A thread-safe bounded counter that coordinates named counters across worker threads.
"""

import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter that maintains named sub-counters and enforces a
    maximum total count across all names.
    """

    def __init__(self, max_total: int) -> None:
        """
        Initialize the BoundedCounter.

        :param max_total: The maximum allowed total count across all names.
        :raises ValueError: If max_total is not positive.
        """
        if max_total <= 0:
            raise ValueError(f"max_total must be positive, got {max_total}")

        self._max_total = max_total
        self._counts: Dict[str, int] = {}
        self._total: int = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increment the named counter by one and return the new value for that name.

        :param name: The name of the counter to increment.
        :returns: The new value of the named counter after incrementing.
        :raises OverflowError: If incrementing would cause the total to exceed max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Incrementing '{name}' would exceed max_total of {self._max_total}"
                )
            self._total += 1
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            return new_value

    def total(self) -> int:
        """
        Return the total count across all names.

        :returns: The sum of all named counters.
        """
        with self._lock:
            return self._total

    def snapshot(self) -> Dict[str, int]:
        """
        Return a copy of nonzero counts by name.

        :returns: A dictionary mapping name to count for all names with nonzero counts.
        """
        with self._lock:
            return {name: count for name, count in self._counts.items() if count != 0}
