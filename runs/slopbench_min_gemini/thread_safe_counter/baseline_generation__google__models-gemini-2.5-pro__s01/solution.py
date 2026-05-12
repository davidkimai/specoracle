import threading
from typing import Dict

class BoundedCounter:
    """
    A thread-safe counter that tracks multiple named counts up to a shared maximum total.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum allowable sum of all counters. Must be a
                       positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total = max_total
        self._counts: Dict[str, int] = {}
        self._total_count = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments the counter for the given name by one.

        This operation is atomic. It first checks if the increment would
        exceed the max_total and only proceeds if it would not.

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
                    f"Cannot increment counter '{name}', total count would exceed "
                    f"maximum of {self._max_total}"
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
            The sum of all named counters.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with nonzero values.

        This operation is thread-safe and returns a copy to prevent mutation
        of the internal state.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # The internal _counts dictionary only stores keys that have been
            # incremented, so all values are guaranteed to be non-zero.
            # .copy() creates a shallow copy, which is sufficient as keys
            # (str) and values (int) are immutable.
            return self._counts.copy()
