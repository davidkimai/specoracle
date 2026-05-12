"""
A thread-unsafe token bucket rate limiter for enforcing usage policies.
"""

import time
from typing import Callable, Optional

__all__ = ["TokenBucketEnforcer"]


class TokenBucketEnforcer:
    """
    Enforces a rate limit using the token bucket algorithm.

    This implementation is not thread-safe. If an instance is used
    concurrently from multiple threads, access must be synchronized
    externally.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes the TokenBucketEnforcer.

        Args:
            capacity: The maximum number of tokens the bucket can hold.
            refill_rate: The number of tokens to add per second.
            now: An optional callable that returns the current time as a float.
                 If None, `time.time` is used. This is useful for testing.

        Raises:
            ValueError: If capacity or refill_rate are not positive numbers.
        """
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        if not isinstance(refill_rate, (int, float)) or refill_rate <= 0:
            raise ValueError("Refill rate must be a positive number.")

        self._capacity: int = capacity
        self._refill_rate: float = float(refill_rate)
        self._now_func: Callable[[], float] = now if now is not None else time.time

        self._tokens: float = float(self._capacity)
        self._last_refill_time: float = self._now_func()

    def _refill(self) -> None:
        """Refills tokens based on the elapsed time since the last refill."""
        current_time = self._now_func()
        elapsed_time = max(0.0, current_time - self._last_refill_time)

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self._refill_rate
            self._tokens = min(self._capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Checks if a request with a given cost is allowed.

        If allowed, consumes the tokens and returns True. Otherwise, returns False.
        The token bucket is refilled before the check.

        Args:
            cost: The number of tokens required for the request. Defaults to 1.

        Returns:
            True if the request is allowed, False otherwise.

        Raises:
            ValueError: If cost is not a positive integer.
        """
        if not isinstance(cost, int) or cost <= 0:
            raise ValueError("Cost must be a positive integer.")

        self._refill()

        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
