"""
token_bucket_enforcer.py

A token-bucket rate limiter.

TokenBucketEnforcer(capacity, refill_rate, *, burst=0, now=None)

    capacity    – maximum number of tokens the bucket can hold (int > 0)
    refill_rate – tokens added per second (float > 0)
    burst       – additional tokens added to maximum capacity (int >= 0);
                  defaults to 0 (original behaviour)
    now         – zero-argument callable returning current time in seconds;
                  defaults to time.monotonic

allow(cost=1) -> bool

    Refills tokens proportional to elapsed time since the last call,
    then consumes `cost` tokens if available.  Returns True on success,
    False when the bucket does not hold enough tokens.  The bucket level
    never exceeds capacity + burst.
"""

import time


class TokenBucketEnforcer:
    def __init__(self, capacity: int, refill_rate: float, *, burst: int = 0, now=None):
        if capacity <= 0:
            raise ValueError(f"capacity must be > 0, got {capacity!r}")
        if refill_rate <= 0:
            raise ValueError(f"refill_rate must be > 0, got {refill_rate!r}")
        if burst < 0:
            raise ValueError(f"burst must be >= 0, got {burst!r}")

        self._capacity = capacity
        self._refill_rate = refill_rate
        self._burst = burst
        self._max_tokens = float(capacity + burst)
        self._now = now if now is not None else time.monotonic

        self._tokens: float = self._max_tokens
        self._last_refill: float = self._now()

    def _refill(self) -> None:
        current = self._now()
        elapsed = current - self._last_refill
        if elapsed < 0:
            elapsed = 0
        self._tokens = min(
            self._max_tokens,
            self._tokens + elapsed * self._refill_rate,
        )
        self._last_refill = current

    def allow(self, cost: int = 1) -> bool:
        if cost < 0:
            raise ValueError(f"cost must be >= 0, got {cost!r}")
        self._refill()
        if cost > self._tokens:
            return False
        self._tokens -= cost
        return True
