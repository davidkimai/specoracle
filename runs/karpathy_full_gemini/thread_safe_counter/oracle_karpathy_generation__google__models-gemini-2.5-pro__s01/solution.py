import collections
import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter for coordinating named counters across worker threads,
    enforcing a maximum total count.
    """

    def __init__(self, max_total: int):
        """
        Initializes a BoundedCounter.

        Args:
            max_total: The maximum permissible total count across all names.

        Raises:
            ValueError: If max_total is not positive.
        """
        if max_total <= 0:
            raise ValueError("max_total must be positive")

        self._max_total = max_total
        self._lock = threading.Lock()
        self._counts = collections.defaultdict(int)
        self._current_total = 0

    def increment(self, name: str) -> int:
        """
        Increments the named counter by one.

        This operation is atomic. If the total count across all names would
        exceed the configured maximum, an OverflowError is raised.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If the increment would cause the total count to
                           exceed max_total.
        """
        with self._lock:
            if self._current_total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment, total count has reached the "
                    f"maximum of {self._max_total}"
                )
            self._counts[name] += 1
            self._current_total += 1
            return self._counts[name]

    def total(self) -> int:
        """
        Returns the total count across all names.

        This operation is atomic.

        Returns:
            The current total count.
        """
        with self._lock:
            return self._current_total

    def snapshot(self) -> Dict[str, int]:
        """
        Returns a copy of the current counts for all names.

        The returned dictionary contains only names with nonzero counts.
        This operation is atomic and does not expose internal mutable state.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # The dict() constructor creates a shallow copy. Since values are
            # immutable integers, this is sufficient to prevent mutation
            # of internal state. All stored counts are guaranteed to be non-zero
            # because they are only created and incremented.
            return dict(self._counts)
