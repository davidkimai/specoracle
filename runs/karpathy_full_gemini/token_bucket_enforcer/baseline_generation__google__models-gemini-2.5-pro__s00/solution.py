"""
A module for implementing a token bucket rate-limiting algorithm.

This module provides the TokenBucketEnforcer class, which can be used to
enforce rate limits on operations.
"""

import time
from typing import Callable, Optional


class TokenBucketEnforcer:
    """
    A token bucket implementation for rate limiting.

    This class provides a thread-unsafe token bucket algorithm. It is useful for
    enforcing a limit on the rate of some action. The bucket has a fixed
    capacity and is refilled with tokens at a constant rate. An action is
    allowed if there are enough tokens in the bucket to cover its cost.

    For thread-safe operations, an external lock must be used to protect
    calls to the `allow` method.
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
            capacity: The maximum number of tokens the bucket can hold. Must be
                      a positive integer.
            refill_rate: The number of tokens to add per second. Must be a
                         positive number.
            now: An optional callable that returns the current time as a float
                 (e.g., time.time). Primarily used for testing. If None,
                 `time.time` is used.

        Raises:
            ValueError: If capacity or refill_rate are not positive numbers.
        """
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        if not isinstance(refill_rate, (int, float)) or refill_rate <= 0:
            raise ValueError("Refill rate must be a positive number.")

        self._capacity: int = capacity
        self._refill_rate: float = refill_rate
        self._now: Callable[[], float] = now if now is not None else time.time

        self._tokens: float = float(self._capacity)
        self._last_refill_time: float = self._now()

    def _refill(self) -> None:
        """
        Calculates and adds new tokens to the bucket based on elapsed time.
        """
        current_time = self._now()
        elapsed_time = current_time - self._last_refill_time

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self._refill_rate
            self._tokens = min(self._capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Checks if a request with a given cost is allowed.

        This method first refills the bucket with tokens based on the time
        elapsed since the last call. Then, it checks if the bucket contains
        enough tokens to satisfy the cost. If it does, the cost is deducted
        from the bucket and the method returns True. Otherwise, it returns
        False.

        Args:
            cost: The number of tokens required for the action. Defaults to 1.
                  Must be a positive integer.

        Returns:
            True if the action is allowed, False otherwise.

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
