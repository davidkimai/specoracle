# token_bucket_enforcer.py

"""
A thread-unsafe token bucket implementation for rate limiting.

This module provides a TokenBucketEnforcer class that can be used to enforce
rate limits based on the token bucket algorithm.
"""

import time
from typing import Callable, Optional


class TokenBucketEnforcer:
    """
    Implements the token bucket algorithm for rate limiting.

    This class maintains a bucket of tokens that are refilled at a constant
    rate. Each request consumes a certain number of tokens. If the bucket
    does not have enough tokens to satisfy a request, the request is denied.
    The number of tokens in the bucket can never exceed its capacity.

    This implementation is not thread-safe. If used in a multi-threaded
    environment, access to the `allow` method should be synchronized.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Optional[Callable[[], float]] = None
    ):
        """
        Initializes the TokenBucketEnforcer.

        Args:
            capacity: The maximum number of tokens the bucket can hold. Must be
                      a positive integer.
            refill_rate: The rate at which tokens are added to the bucket per
                         second. Must be a positive number.
            now: An optional callable that returns the current time in seconds,
                 used for dependency injection in tests. If None, `time.monotonic`
                 is used, which is suitable for production.
        """
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer.")
        if not isinstance(refill_rate, (int, float)) or refill_rate <= 0:
            raise ValueError("refill_rate must be a positive number.")

        self.capacity: int = capacity
        self.refill_rate: float = float(refill_rate)
        
        self._now: Callable[[], float] = now if now is not None else time.monotonic
        self._tokens: float = float(self.capacity)
        self._last_update_time: float = self._now()

    def allow(self, cost: int = 1) -> bool:
        """
        Determines if a request with a given cost should be allowed.

        This method first refills the bucket with tokens based on the time
        elapsed since the last call. It then checks if the bucket contains
        enough tokens to cover the cost. If it does, the tokens are consumed,
        and the method returns True. Otherwise, the request is denied, and the
        method returns False.

        Args:
            cost: The number of tokens required for the operation. Must be a
                  non-negative integer. Defaults to 1.

        Returns:
            True if the request is allowed, False otherwise.
        """
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("cost must be a non-negative integer.")

        # Refill tokens based on the elapsed time.
        current_time = self._now()
        elapsed_time = max(0.0, current_time - self._last_update_time)

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self.refill_rate
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_update_time = current_time

        # Check if there are enough tokens and consume them if so.
        if cost <= self._tokens:
            self._tokens -= cost
            return True
        else:
            return False
