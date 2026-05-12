import time


class TokenBucketEnforcer:
    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic
        self._tokens = float(capacity)
        self._last = self._now()

    def allow(self, cost: int = 1) -> bool:
        current = self._now()
        elapsed = current - self._last
        self._last = current
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
        if cost <= self._tokens:
            self._tokens -= cost
            return True
        return False
