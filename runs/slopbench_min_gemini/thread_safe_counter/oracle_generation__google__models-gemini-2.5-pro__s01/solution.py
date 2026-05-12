# thread_safe_counter.py

"""
A thread-safe, bounded counter for coordinating named counts across workers.
"""

import threading
from typing import Dict

__all__ = ["BoundedCounter"]


class BoundedCounter:
    """
    A thread-safe counter for named items with a shared total maximum.

    This class allows multiple threads to safely increment named counters
    while ensuring that the sum of all counts does not exceed a specified
    maximum.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum sum of all counts. Must be positive.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._counts: Dict[str, int] = {}
        self._total_count: int = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        This operation is atomic and thread-safe.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If incrementing would cause the total count to
                           exceed the max_total limit.
        """
        with self._lock:
            if self._total_count >= self._max_total:
                msg = (
                    f"Cannot increment '{name}'. "
                    f"Total count {self._total_count} has reached the "
                    f"maximum of {self._max_total}."
                )
                raise OverflowError(msg)

            current_value = self._counts.get(name, 0)
            new_value = current_value + 1
            self._counts[name] = new_value
            self._total_count += 1
            return new_value

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is thread-safe.

        Returns:
            The sum of all individual counts.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with nonzero values.

        This operation is thread-safe and returns a copy of the internal state,
        so modifications to the returned dictionary will not affect the counter.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # The dictionary comprehension creates a new dictionary, ensuring
            # that a copy is returned, thus preventing mutation of internal state.
            return {
                name: count
                for name, count in self._counts.items()
                if count > 0
            }
