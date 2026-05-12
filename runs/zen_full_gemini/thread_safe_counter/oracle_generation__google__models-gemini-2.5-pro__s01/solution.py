import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter for named items with a total maximum capacity.

    This class coordinates counting across multiple worker threads, ensuring that
    the sum of all named counts does not exceed a specified maximum. All public
    methods are thread-safe.
    """

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

        self._max_total: int = max_total
        self._lock: threading.Lock = threading.Lock()
        self._counts: Dict[str, int] = {}
        self._total_count: int = 0

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        This operation is atomic. If the total count across all names has already
        reached the maximum capacity, this method will raise an error.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If incrementing would cause the total count to exceed
                           the max_total capacity.
        """
        with self._lock:
            if self._total_count >= self._max_total:
                raise OverflowError(
                    "Cannot increment, total count would exceed "
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

        Returns:
            The sum of all individual counts.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names.

        The returned dictionary contains only names with a non-zero count.
        This method returns a shallow copy to prevent mutation of the
        counter's internal state.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # Since counts are only ever incremented from zero, all entries in
            # self._counts are guaranteed to be non-zero. A simple copy is
            # sufficient and correct according to the requirements.
            return self._counts.copy()
