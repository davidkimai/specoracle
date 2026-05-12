import threading
from typing import Dict


class BoundedCounter:
    """A thread-safe counter for coordinating named counts with a total maximum."""

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum sum of all counter values.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._total_count = 0
        self._counts: Dict[str, int] = {}
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments the named counter by one and returns the new value.

        This operation is atomic. If the total count across all names would
        exceed max_total, this method raises an OverflowError and the state
        of the counter is not changed.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the named counter.

        Raises:
            OverflowError: If the total count would exceed max_total.
            TypeError: If the name is not a string.
        """
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        with self._lock:
            if self._total_count >= self._max_total:
                raise OverflowError(
                    f"Incrementing would exceed max_total of {self._max_total}"
                )

            self._total_count += 1
            self._counts[name] = self._counts.get(name, 0) + 1
            return self._counts[name]

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is atomic.

        Returns:
            The sum of all counter values.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the nonzero counts by name.

        The returned dictionary is a snapshot and will not reflect subsequent
        changes to the counter. It is safe for the caller to modify.

        Returns:
            A dictionary mapping counter names to their current values.
        """
        with self._lock:
            # A new dictionary is created to prevent exposing internal state and
            # to adhere to the "nonzero" requirement.
            return {
                name: count for name, count in self._counts.items() if count > 0
            }
