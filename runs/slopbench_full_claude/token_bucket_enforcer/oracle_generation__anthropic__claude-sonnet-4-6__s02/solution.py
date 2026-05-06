"""
token_bucket_enforcer.py

A token-bucket rate limiter.

TokenBucketEnforcer(capacity, refill_rate, *, now=None)

    capacity    -- maximum number of tokens the bucket can hold (int > 0)
    refill_rate -- tokens added per second (float > 0)
    now         -- callable returning current time as a float (default: time.monotonic)

Method
------
allow(cost=1) -> bool
    Attempt to consume `cost` tokens.
    Returns True and deducts the tokens when enough are available.
    Returns False without modifying state when tokens are insufficient.
"""

import time


class TokenBucketEnforcer:
    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity!r}")
        if refill_rate <= 0:
            raise ValueError(f"refill_rate must be positive, got {refill_rate!r}")

        self._capacity = capacity
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic

        self._tokens: float = float(capacity)
        self._last_refill: float = self._now()

    def _refill(self) -> None:
        current_time = self._now()
        elapsed = current_time - self._last_refill
        if elapsed > 0:
            self._tokens = min(
                float(self._capacity),
                self._tokens + elapsed * self._refill_rate,
            )
            self._last_refill = current_time

    def allow(self, cost: int = 1) -> bool:
        if cost < 0:
            raise ValueError(f"cost must be non-negative, got {cost!r}")
        self._refill()
        if cost > self._tokens:
            return False
        self._tokens -= cost
        return True
