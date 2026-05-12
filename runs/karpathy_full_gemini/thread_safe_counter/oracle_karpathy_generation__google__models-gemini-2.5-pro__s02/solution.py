import threading
from typing import Dict

class BoundedCounter:
    """
    A thread-safe counter that tracks counts for named items up to a total maximum.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum total count allowed across all names.

        Raises:
            ValueError: If max_total is not positive.
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

        Args:
            name: The name of the counter to increment.

        Returns:
            The new count for the given name.

        Raises:
            OverflowError: If incrementing would cause the total count to exceed
                           the max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError("total count would exceed max_total")
            
            self._total += 1
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            return new_value

    def total(self) -> int:
        """
        Returns the total count across all names.

        Returns:
            The sum of all named counts.
        """
        with self._lock:
            return self._total

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a snapshot of the current counts for all names.

        The returned dictionary is a copy and can be safely mutated.
        Only names with non-zero counts are included.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # Since counts are only incremented from 0, all stored counts
            # will be non-zero.
            return self._counts.copy()
