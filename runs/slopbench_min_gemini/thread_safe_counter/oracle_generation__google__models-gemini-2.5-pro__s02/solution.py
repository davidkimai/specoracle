import threading
from typing import Dict


class BoundedCounter:
    """A thread-safe counter for named items with a total maximum capacity."""

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum sum of all counts. Must be a positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._lock = threading.Lock()
        self._counts: Dict[str, int] = {}
        self._total_count = 0

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If incrementing would cause the total count to
                           exceed max_total.
            TypeError: If name is not a string.
        """
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        with self._lock:
            if self._total_count >= self._max_total:
                message = (
                    "Cannot increment, total count would exceed "
                    f"maximum of {self._max_total}"
                )
                raise OverflowError(message)

            current_value = self._counts.get(name, 0)
            new_value = current_value + 1
            self._counts[name] = new_value
            self._total_count += 1
            return new_value

    def total(self) -> int:
        """
        Returns the total count across all names.

        Returns:
            The sum of all counter values.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with non-zero values.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # The .copy() method creates a shallow copy. Since the keys (str)
            # and values (int) are immutable, this is effectively a deep,
            # independent copy of the counter state.
            return self._counts.copy()
