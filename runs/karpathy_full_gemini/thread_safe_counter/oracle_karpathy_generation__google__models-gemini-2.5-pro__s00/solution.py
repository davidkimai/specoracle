# thread_safe_counter.py

import threading
from typing import Dict

class BoundedCounter:
    """A thread-safe counter for coordinating named counts up to a total maximum.

    This class provides a way to increment named counters while ensuring the sum
    of all counts does not exceed a specified maximum. All operations that
    access or modify the counter state are thread-safe.
    """

    def __init__(self, max_total: int):
        """Initializes a BoundedCounter.

        Args:
            max_total: The maximum allowable sum of all named counts. Must be
                       a positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._lock = threading.Lock()
        self._counts: Dict[str, int] = {}
        self._current_total: int = 0

    def increment(self, name: str) -> int:
        """Increments a named counter by one and returns its new value.

        This operation is atomic. If the increment would cause the total count
        to exceed max_total, the operation fails and raises an error.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the named counter after the increment.

        Raises:
            OverflowError: If the total count across all names would exceed
                           the configured max_total.
        """
        with self._lock:
            if self._current_total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment, total count would exceed max_total ({self._max_total})"
                )

            # Increment the specific and total counts
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            self._current_total += 1

            return new_value

    def total(self) -> int:
        """Returns the total count across all names.

        This operation is atomic.

        Returns:
            The sum of all named counters.
        """
        with self._lock:
            return self._current_total

    def snapshot(self) -> Dict[str, int]:
        """Returns a snapshot of the current counts for all non-zero names.

        The returned dictionary is a copy and can be safely read while other
        threads modify the counter.

        This operation is atomic.

        Returns:
            A dictionary mapping counter names to their current non-zero counts.
        """
        with self._lock:
            # Since this implementation only supports incrementing, all stored
            # counts are guaranteed to be non-zero. A simple copy is sufficient.
            return self._counts.copy()
