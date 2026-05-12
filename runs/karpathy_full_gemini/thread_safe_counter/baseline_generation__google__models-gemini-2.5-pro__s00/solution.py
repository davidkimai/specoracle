"""
A thread-safe, bounded counter for coordinating named counters across worker threads.
"""

import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter that tracks counts for different names up to a total maximum.

    This class is designed for use in multi-threaded environments where multiple
    workers need to increment named counters without exceeding a collective limit.
    All methods that access or modify state are protected by a lock.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum sum of all counts across all names. Must be
                       a positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._lock = threading.Lock()
        self._total_count = 0
        self._named_counts: Dict[str, int] = {}

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        This operation is atomic. If incrementing would cause the total count
        to exceed max_total, an OverflowError is raised.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If the total count across all names would exceed
                           the max_total limit.
        """
        with self._lock:
            if self._total_count >= self._max_total:
                raise OverflowError(
                    f"Incrementing would exceed max_total of {self._max_total}"
                )

            self._total_count += 1
            new_value = self._named_counts.get(name, 0) + 1
            self._named_counts[name] = new_value
            return new_value

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is atomic and reads the most recent total.

        Returns:
            The sum of all individual counts.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a snapshot of the current counts for all names with a count > 0.

        The returned dictionary is a copy and can be safely read while other
        threads modify the counter, preventing race conditions and exposure
        of internal mutable state.

        Returns:
            A dictionary mapping names to their current non-zero counts.
        """
        with self._lock:
            # A copy is returned to prevent mutation of internal state.
            # The internal dictionary only ever stores non-zero counts.
            return self._named_counts.copy()
