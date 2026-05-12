import time
from typing import Callable


def _validate_non_negative_integer(value: int, name: str) -> None:
    """Checks if a value is a non-negative integer."""
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer.")
    if value < 0:
        raise ValueError(f"{name} must not be negative.")


def _validate_non_negative_number(value: float, name: str) -> None:
    """Checks if a value is a non-negative number."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number (int or float).")
    if value < 0:
        raise ValueError(f"{name} must not be negative.")


class TokenBucketEnforcer:
    """
    Implements a token bucket algorithm for rate limiting.

    This class allows checking if an action can be performed based on the
    availability of tokens, which are refilled at a constant rate. The bucket
    has a maximum capacity, and tokens that would overflow the capacity are
    discarded.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Callable[[], float] = None,
    ):
        """
        Initializes the TokenBucketEnforcer.

        Args:
            capacity: The maximum number of tokens the bucket can hold.
            refill_rate: The number of tokens to add per second.
            now: An optional callable that returns the current time as a float
                 (e.g., `time.time`). If None, `time.time` is used. This
                 parameter is primarily for testing.

        Raises:
            TypeError: If capacity is not an integer or refill_rate is not a number.
            ValueError: If capacity or refill_rate are negative.
        """
        _validate_non_negative_integer(capacity, "Capacity")
        _validate_non_negative_number(refill_rate, "Refill rate")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self._now = now if now is not None else time.time

        self._tokens: float = float(capacity)
        self._last_refill_time: float = self._now()

    def _refill(self) -> None:
        """Updates the number of tokens based on elapsed time."""
        current_time = self._now()
        elapsed = current_time - self._last_refill_time

        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Checks if a request with a given cost can be allowed.

        This method first refills the bucket based on the time elapsed since the
        last call. Then, it checks if there are enough tokens to cover the cost.
        If allowed, the cost is deducted from the available tokens.

        Args:
            cost: The number of tokens required for the action. Defaults to 1.

        Returns:
            True if the action is allowed, False otherwise.

        Raises:
            TypeError: If cost is not an integer.
            ValueError: If cost is negative.
        """
        _validate_non_negative_integer(cost, "Cost")

        self._refill()

        if cost <= self._tokens:
            self._tokens -= cost
            return True

        return False
