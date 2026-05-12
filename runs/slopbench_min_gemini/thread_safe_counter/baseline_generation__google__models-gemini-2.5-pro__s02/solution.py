import threading
from typing import Dict

__all__ = ["BoundedCounter"]


class BoundedCounter:
    """
    A thread-safe counter that tracks multiple named counts up to a total maximum.

    This class is designed for coordinating named counters across multiple worker
    threads, ensuring that the total count of all items never exceeds a
    predefined maximum. All operations that access or modify the counter state
    are protected by a lock to guarantee thread safety.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum total count allowed across all names.
                       Must be a positive integer.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")
        self._max_total = max_total
        self._counters: Dict[str, int] = {}
        self._total_count = 0
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increments the count for a given name by one.

        This operation is atomic. If incrementing would cause the total count to
        exceed the configured maximum, an OverflowError is raised.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If the total count would exceed max_total.
        """
        with self._lock:
            if self._total_count >= self._max_total:
                raise OverflowError(
                    f"Increment would exceed max_total of {self._max_total}"
                )

            new_value = self._counters.get(name, 0) + 1
            self._counters[name] = new_value
            self._total_count += 1
            return new_value

    def total(self) -> int:
        """
        Returns the total count across all named counters.

        This operation is thread-safe.

        Returns:
            The current total count.
        """
        with self._lock:
            return self._total_count

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names with non-zero counts.

        This method provides a point-in-time, thread-safe snapshot of the
        counter state. The returned dictionary is a copy, so modifications to
        it will not affect the internal state of the counter.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # A shallow copy is sufficient as keys (str) and values (int)
            # are immutable.
            return self._counters.copy()
