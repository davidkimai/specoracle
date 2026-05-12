"""
A module providing a thread-safe, bounded counter for named items.
"""

import threading
from typing import Dict

class BoundedCounter:
    """
    A thread-safe counter for coordinating named counts across worker threads,
    subject to a total maximum count.

    This class ensures that all operations are atomic and that the total
    count across all named items does not exceed a specified maximum.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum permissible total count across all names.
                       Must be a positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._lock = threading.Lock()
        self._counts: Dict[str, int] = {}
        self._total_count: int = 0

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        This operation is atomic. If incrementing would cause the total count
        to exceed the configured max_total, an OverflowError is raised.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If the total count would exceed max_total.
        """
        with self._lock:
            if self._total_count >= self._max_total:
                raise OverflowError(
                    f"Cannot increment: total count {self._total_count} "
                    f"would exceed max_total {self._max_total}"
                )

            self._total_count += 1
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            return new_value

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is thread-safe.

        Returns:
            The current total count.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with non-zero counts.

        This method provides a point-in-time, thread-safe snapshot of the
        counter's state. The returned dictionary is a copy and can be safely
        mutated without affecting the counter's internal state.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # Since counts are only ever incremented from zero, any entry in
            # self._counts will have a non-zero value.
            return self._counts.copy()
