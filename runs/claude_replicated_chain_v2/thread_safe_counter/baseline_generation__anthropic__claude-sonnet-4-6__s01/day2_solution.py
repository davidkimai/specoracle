"""
thread_safe_counter.py

A thread-safe bounded counter that coordinates named counters across worker threads.
"""

import threading
from typing import Dict


class BoundedCounter:
    """
    A thread-safe counter that tracks named counters with a global maximum total.

    Parameters
    ----------
    max_total : int
        The maximum allowed total count across all named counters.
        Must be a positive integer.

    Raises
    ------
    ValueError
        If max_total is not a positive integer.
    """

    def __init__(self, max_total: int) -> None:
        if not isinstance(max_total, int) or max_total <= 0:
            raise ValueError(
                f"max_total must be a positive integer, got {max_total!r}"
            )
        self._max_total: int = max_total
        self._counts: Dict[str, int] = {}
        self._total: int = 0
        self._lock: threading.Lock = threading.Lock()

    def increment(self, name: str) -> int:
        """
        Increment the named counter by one and return its new value.

        Parameters
        ----------
        name : str
            The name of the counter to increment.

        Returns
        -------
        int
            The new value of the named counter after incrementing.

        Raises
        ------
        OverflowError
            If incrementing would cause the total count to exceed max_total.
        """
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError(
                    f"Cannot increment '{name}': total count would exceed "
                    f"max_total ({self._max_total})"
                )
            self._total += 1
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            return new_value

    def decrement(self, name: str) -> int:
        """
        Decrement the named counter by one and return its new value.

        Parameters
        ----------
        name : str
            The name of the counter to decrement.

        Returns
        -------
        int
            The new value of the named counter after decrementing.

        Raises
        ------
        KeyError
            If the name is absent or its current value is already zero.
        """
        with self._lock:
            current = self._counts.get(name, 0)
            if current == 0:
                raise KeyError(
                    f"Cannot decrement '{name}': counter is absent or already zero"
                )
            new_value = current - 1
            self._total -= 1
            if new_value == 0:
                del self._counts[name]
            else:
                self._counts[name] = new_value
            return new_value

    def total(self) -> int:
        """
        Return the total count across all named counters.

        Returns
        -------
        int
            The sum of all named counter values.
        """
        with self._lock:
            return self._total

    def snapshot(self) -> Dict[str, int]:
        """
        Return a copy of the current nonzero counts by name.

        Returns
        -------
        dict[str, int]
            A shallow copy of the internal counts dictionary containing only
            entries with nonzero values.
        """
        with self._lock:
            return {name: count for name, count in self._counts.items() if count != 0}
