# token_bucket_enforcer.py

"""
A thread-unsafe implementation of the token bucket algorithm for rate limiting.
"""

import time
from typing import Callable, Optional

__all__ = ["TokenBucketEnforcer"]


class TokenBucketEnforcer:
    """
    Implements a token bucket algorithm for rate limiting.

    This class provides a simple way to enforce a limit on the frequency of
    events. It is configured with a capacity and a refill rate. Each call to
    the `allow()` method attempts to consume one or more tokens. If the bucket
    has enough tokens, the request is allowed. The bucket is refilled over

    time based on the specified rate.

    Note: This implementation is not thread-safe. If used in a multi-threaded
    environment, external locking is required.
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
            capacity: The maximum number of tokens the bucket can hold.
                      Must be a positive integer.
            refill_rate: The number of tokens added to the bucket per second.
                         Must be a positive number.
            now: An optional callable that returns the current time as a float
                 (e.g., time.monotonic). Defaults to time.time. This is
                 primarily for testing purposes.
        """
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if not isinstance(refill_rate, (int, float)) or refill_rate <= 0:
            raise ValueError("refill_rate must be a positive number")

        self.capacity: int = capacity
        self.refill_rate: float = refill_rate
        self._now: Callable[[], float] = now if now is not None else time.time

        self._tokens: float = float(self.capacity)
        self._last_refill_time: float = self._now()

    def _refill(self) -> None:
        """Refills tokens based on the elapsed time since the last operation."""
        current_time = self._now()
        elapsed_time = current_time - self._last_refill_time

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self.refill_rate
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

    def allow(self, cost: int = 1) -> bool:
        """
        Determines if a request with a given cost should be allowed.

        This method first refills the bucket based on the time that has elapsed
        since the last call. Then, it checks if the bucket contains enough
        tokens to satisfy the cost. If it does, the tokens are consumed and
        the method returns True. Otherwise, the request is denied and the
        method returns False without changing the token count.

        Args:
            cost: The number of tokens required for the request. Defaults to 1.
                  Must be a non-negative integer.

        Returns:
            True if the request is allowed, False otherwise.
        """
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("cost must be a non-negative integer")

        self._refill()

        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
