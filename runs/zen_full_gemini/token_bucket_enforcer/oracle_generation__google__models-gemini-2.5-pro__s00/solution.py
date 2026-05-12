import time
from typing import Callable


def _validate_positive_integer(value: int, name: str) -> None:
    """Checks if a value is a positive integer."""
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def _validate_positive_number(value: float, name: str) -> None:
    """Checks if a value is a positive number."""
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number.")


def _validate_non_negative_integer(value: int, name: str) -> None:
    """Checks if a value is a non-negative integer."""
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer.")


class TokenBucketEnforcer:
    """
    Enforces a rate limit using the token bucket algorithm.

    This implementation is not thread-safe. Concurrent calls to `allow`
    from multiple threads may lead to race conditions. External locking
    is required for thread-safe operation.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Callable[[], float] = None,
    ):
        """
        Initializes the token bucket.

        Args:
            capacity: The maximum number of tokens the bucket can hold.
            refill_rate: The number of tokens to add per second.
            now: An optional callable that returns the current time as a float
                 (e.g., seconds since the epoch). Defaults to `time.monotonic`.
                 Using a monotonic clock is recommended to prevent issues with
                 system time changes.

        Raises:
            ValueError: If capacity or refill_rate are not positive numbers.
        """
        _validate_positive_integer(capacity, "Capacity")
        _validate_positive_number(refill_rate, "Refill rate")

        self.capacity = capacity
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic

        self._tokens: float = float(self.capacity)
        self._last_refill_time: float = self._now()

    def _refill_tokens(self) -> None:
        """Calculates and adds new tokens based on elapsed time."""
        current_time = self._now()
        elapsed_time = current_time - self._last_refill_time

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self._refill_rate
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Determines if an action with a given cost is permitted.

        If permitted, the specified number of tokens is consumed from the bucket.
        The bucket is refilled with any tokens that have accrued since the last
        call before checking for available tokens.

        Args:
            cost: The number of tokens required for the action.

        Returns:
            True if enough tokens are available, False otherwise.

        Raises:
            ValueError: If cost is a negative number.
        """
        _validate_non_negative_integer(cost, "Cost")

        self._refill_tokens()

        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
