# -*- coding: utf-8 -*-
"""
A thread-safe, bounded counter for coordinating named counters across worker threads.
"""

import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter for named items with a total maximum bound.

    This class allows multiple threads to safely increment named counters,
    ensuring that the total count across all names does not exceed a specified
    maximum.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter with a maximum total count.

        Args:
            max_total: The maximum allowable sum of all counter values.
                       Must be a positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total: int = max_total
        self._counts: Dict[str, int] = {}
        self._total_count: int = 0
        self._lock: threading.Lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments the counter for the given name by one.

        This operation is atomic and thread-safe.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If incrementing the counter would cause the total
                           count to exceed max_total.
        """
        with self._lock:
            if self._total_count >= self._max_total:
                raise OverflowError(
                    f"Cannot increment: total count would exceed max_total ({self._max_total})"
                )

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
            The sum of all counter values.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with nonzero values.

        This operation is thread-safe and returns a copy to prevent modification
        of the internal state. Since counts can only be incremented, all
        entries in the internal dictionary will have a nonzero value.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            return self._counts.copy()
