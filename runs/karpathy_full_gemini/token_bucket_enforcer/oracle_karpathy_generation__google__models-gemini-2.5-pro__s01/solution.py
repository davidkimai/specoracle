import time
from typing import Callable, Optional

class TokenBucketEnforcer:
    """
    Implements a token bucket algorithm for rate limiting.

    This class maintains a bucket of tokens that refills at a constant rate.
    Requests to perform an action "consume" a specified number of tokens. If the
    bucket does not have enough tokens, the request is denied. The number of
    tokens in the bucket will never exceed its capacity.
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
            refill_rate: The rate at which tokens are added to the bucket,
                         in tokens per second.
            now: An optional callable that returns the current time as a float
                 (e.g., time.monotonic). Defaults to time.monotonic.
        """
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer.")
        if capacity < 0:
            raise ValueError("capacity must be non-negative.")
        if not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be a number.")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative.")

        self._capacity = capacity
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic

        self._tokens: float = float(self._capacity)
        self._last_refill_time: float = self._now()

    def allow(self, cost: int = 1) -> bool:
        """
        Determines if a request with a given cost should be allowed.

        This method first refills the bucket based on elapsed time, then checks
        if there are enough tokens to cover the cost. If allowed, the cost is
        deducted from the bucket.

        Args:
            cost: The number of tokens required for the action. Defaults to 1.

        Returns:
            True if the request is allowed, False otherwise.
        """
        if not isinstance(cost, int):
            raise TypeError("cost must be an integer.")
        if cost < 0:
            raise ValueError("cost must be non-negative.")

        # Refill tokens based on elapsed time
        current_time = self._now()
        elapsed_time = current_time - self._last_refill_time

        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self._refill_rate
            self._tokens = min(self._capacity, self._tokens + tokens_to_add)
            self._last_refill_time = current_time

        # Check if there are enough tokens and consume them if so
        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
