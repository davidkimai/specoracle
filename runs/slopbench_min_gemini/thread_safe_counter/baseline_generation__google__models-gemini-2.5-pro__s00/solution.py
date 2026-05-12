"""
A thread-safe, bounded, multi-named counter.
"""

import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter that tracks multiple named counts up to a total maximum.

    This class allows multiple threads to safely increment named counters while
    ensuring that the sum of all counts does not exceed a specified maximum.
    """

    def __init__(self, max_total: int):
        """
        Initializes the BoundedCounter.

        Args:
            max_total: The maximum allowable sum of all counts. Must be a
                       positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")
        self._max_total = max_total
        self._counts: Dict[str, int] = {}
        self._current_total = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments a named counter by one.

        This operation is atomic. If incrementing would cause the total count
        to exceed the configured maximum, an OverflowError is raised.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If the total count across all names would exceed
                           max_total.
        """
        with self._lock:
            if self._current_total >= self._max_total:
                raise OverflowError(
                    f"Total count cannot exceed max_total ({self._max_total})"
                )

            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            self._current_total += 1

            return new_value

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is thread-safe.

        Returns:
            The sum of all counter values.
        """
        with self._lock:
            return self._current_total

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a snapshot of the current counts for all names.

        The returned dictionary is a copy and can be safely read without
        interfering with the counter's operations. It includes only counters
        with a non-zero value.

        Returns:
            A dictionary mapping counter names to their current values.
        """
        with self._lock:
            # Since counts are only ever incremented from zero, any existing
            # key in self._counts will have a non-zero (positive) value.
            # A simple copy satisfies the "nonzero counts" requirement.
            return self._counts.copy()
