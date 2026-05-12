import collections
import threading


class BoundedCounter:
    """A thread-safe counter for named items with a total bound.

    This class provides a way to manage multiple named counters that share a
    collective maximum value. All operations that modify or read counter state
    are protected by a lock to ensure thread safety.
    """

    def __init__(self, max_total: int):
        """Initializes a BoundedCounter.

        Args:
            max_total: The maximum allowed sum of all counter values.

        Raises:
            ValueError: If max_total is not a positive integer.
        """
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError("max_total must be a positive integer")

        self._max_total: int = max_total
        self._lock: threading.Lock = threading.Lock()
        self._counts: collections.defaultdict[str, int] = collections.defaultdict(int)
        self._total: int = 0

    def increment(self, name: str) -> int:
        """Increments the counter for a given name by one.

        This operation is atomic. If the increment would cause the total count
        to exceed max_total, the operation fails and no counters are changed.

        Args:
            name: The name of the counter to increment.

        Returns:
            The new value of the counter for the given name.

        Raises:
            OverflowError: If the total count is already at its maximum.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment, total count has reached "
                    f"the maximum of {self._max_total}"
                )

            self._counts[name] += 1
            self._total += 1
            return self._counts[name]

    def total(self) -> int:
        """Returns the total count across all names.

        This operation is thread-safe.

        Returns:
            The sum of all counter values.
        """
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        """Returns a copy of the current counts for all names.

        The returned dictionary contains only names with non-zero counts.
        This operation is thread-safe and returns a distinct copy, so the
        internal state cannot be mutated by the caller.

        Returns:
            A dictionary mapping names to their current counts.
        """
        with self._lock:
            # Create a new dictionary to ensure the caller cannot mutate
            # the internal defaultdict. Filtering also ensures the contract
            # of returning only non-zero counts is met.
            return {
                name: count for name, count in self._counts.items() if count > 0
            }
