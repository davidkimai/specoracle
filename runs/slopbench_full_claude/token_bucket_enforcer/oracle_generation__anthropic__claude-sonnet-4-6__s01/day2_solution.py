"""
Token Bucket Rate Limiter
"""

import time


class TokenBucketEnforcer:
    """
    Enforce a token-bucket rate limit.

    Parameters
    ----------
    capacity   : maximum number of tokens the bucket can hold
    refill_rate: tokens added per second
    burst      : additional tokens added to the maximum capacity (default 0)
    now        : callable returning current time in seconds (defaults to time.monotonic)
    """

    def __init__(self, capacity: int, refill_rate: float, burst: int = 0, *, now=None):
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity!r}")
        if refill_rate <= 0:
            raise ValueError(f"refill_rate must be positive, got {refill_rate!r}")
        if burst < 0:
            raise ValueError(f"burst must be non-negative, got {burst!r}")

        self._capacity = capacity + burst
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic

        self._tokens: float = float(self._capacity)
        self._last_refill: float = self._now()

    def _refill(self) -> None:
        current = self._now()
        elapsed = current - self._last_refill
        if elapsed > 0:
            self._tokens = min(
                self._capacity,
                self._tokens + elapsed * self._refill_rate,
            )
            self._last_refill = current

    def allow(self, cost: int = 1) -> bool:
        if cost < 0:
            raise ValueError(f"cost must be non-negative, got {cost!r}")
        if cost > self._capacity:
            return False

        self._refill()

        if self._tokens >= cost:
            self._tokens -= cost
            return True

        return False
