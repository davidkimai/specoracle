"""
A module for a thread-safe, bounded counter for named items.
"""

import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter that tracks multiple named counts up to a total maximum.

    This class is designed for coordinating work among multiple threads where a
    global limit on the number of items or tasks must be enforced. All methods
    that access or modify counter state are thread-safe.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum total count across all names. Must be positive.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total: int = max_total
        self._counts: Dict[str, int] = {}
        self._total: int = 0
        self._lock: threading.Lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        This operation is atomic and thread-safe.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If incrementing would cause the total count to exceed
                         the max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Increment failed: total count ({self._total}) would "
                    f"exceed max_total ({self._max_total})"
                )

            new_named_count = self._counts.get(name, 0) + 1
            self._counts[name] = new_named_count
            self._total += 1

            return new_named_count

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is thread-safe.

        Returns:
            The current total count.
        """
        with self._lock:
            return self._total

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with non-zero counts.

        The returned dictionary is a snapshot and will not be affected by
        subsequent changes to the counter. This operation is thread-safe.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # Since counts are only ever incremented from 0, any entry in
            # self._counts will have a value > 0. A simple copy is sufficient
            # and fulfills the "nonzero counts" requirement.
            return self._counts.copy()
