# token_bucket_enforcer.py

"""
A secure and correct implementation of the token bucket algorithm for rate limiting.
"""

import time
from typing import Callable, Optional

__all__ = ["TokenBucketEnforcer"]


class TokenBucketEnforcer:
    """
    Implements a token bucket algorithm for rate limiting.

    This class maintains a bucket of tokens that refills at a constant rate.
    Each call to `allow()` attempts to consume a specified number of tokens.
    If the bucket has enough tokens, the request is allowed, and the tokens
    are consumed. Otherwise, the request is denied. The number of tokens
    in the bucket never exceeds its capacity.
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
            refill_rate: The rate at which tokens are added to the bucket,
                         per second.
            now: An optional callable that returns the current time as a float
                 (e.g., time.time). Used for dependency injection and testing.
                 If None, defaults to time.time.

        Raises:
            ValueError: If capacity or refill_rate are not positive.
        """
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        if not isinstance(refill_rate, (int, float)) or refill_rate <= 0:
            raise ValueError("Refill rate must be a positive number.")

        self.capacity: int = capacity
        self.refill_rate: float = refill_rate

        self._now_func: Callable[[], float] = now if now is not None else time.time
        self._tokens: float = float(self.capacity)
        self._last_refill_time: float = self._now_func()

    def _refill(self) -> None:
        """
        Refills tokens in the bucket based on the elapsed time since the last
        refill. This is a private helper method.
        """
        current_time = self._now_func()
        elapsed_time = current_time - self._last_refill_time

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self.refill_rate
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Attempts to consume a given cost of tokens from the bucket.

        This method first refills the bucket based on the elapsed time since
        the last operation. It then checks if enough tokens are available to
        satisfy the cost. If so, it consumes the tokens and returns True.
        Otherwise, it denies the request and returns False without changing
        the token count.

        Args:
            cost: The number of tokens required for the operation. Defaults to 1.

        Returns:
            True if the operation is allowed, False otherwise.

        Raises:
            ValueError: If cost is not a non-negative integer.
        """
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Cost must be a non-negative integer.")

        self._refill()

        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
