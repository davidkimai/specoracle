# -*- coding: utf-8 -*-
"""
A thread-unsafe implementation of the token bucket algorithm for rate limiting.
"""

import time
from typing import Callable, Optional

__all__ = ["TokenBucketEnforcer"]


class TokenBucketEnforcer:
    """
    Implements a token bucket algorithm for rate limiting.

    This class allows for checking if an action, with a given cost, can be
    performed based on the available tokens in a bucket. The bucket refills
    over time at a specified rate.

    Note: This implementation is not thread-safe. If used in a multi-threaded
    environment, access to its methods should be synchronized.
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
                         in tokens per second.
            now: An optional callable that returns the current time as a float
                 (e.g., time.monotonic). Defaults to time.monotonic. This is
                 primarily for testing purposes.
        """
        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("Capacity must be a non-negative integer")
        if not isinstance(refill_rate, (int, float)) or refill_rate < 0:
            raise ValueError("Refill rate must be a non-negative number")

        self.capacity: int = capacity
        self._refill_rate: float = refill_rate
        self._now: Callable[[], float] = now if now is not None else time.monotonic

        # Use a float for tokens to handle fractional refills accurately.
        self._tokens: float = float(self.capacity)
        self._last_refill_time: float = self._now()

    def _refill(self) -> None:
        """Refills tokens based on the elapsed time since the last update."""
        current_time = self._now()
        elapsed_time = max(0, current_time - self._last_refill_time)

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self._refill_rate
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Checks if a request with a given cost can be allowed.

        If allowed, the cost is deducted from the available tokens. Otherwise,
        the token count remains unchanged. The bucket is refilled with tokens
        accumulated since the last call before the check is performed.

        Args:
            cost: The number of tokens required for the request. Must be a
                  non-negative integer. Defaults to 1.

        Returns:
            True if the cost can be afforded, False otherwise.
        """
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Cost must be a non-negative integer")

        self._refill()

        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
