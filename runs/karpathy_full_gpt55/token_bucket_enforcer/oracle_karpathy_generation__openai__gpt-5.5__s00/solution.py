import time


class TokenBucketEnforcer:
    """Token-bucket rate enforcer.

    Args:
        capacity: Maximum number of tokens the bucket can hold.
        refill_rate: Tokens added per second.
        now: Optional callable returning the current time as a float.

    """

    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")
        if now is None:
            now = time.monotonic
        if not callable(now):
            raise TypeError("now must be callable")

        self.capacity = capacity
        self.refill_rate = float(refill_rate)
        self._now = now
        self._tokens = float(capacity)
        self._last_refill = float(now())

    def allow(self, cost: int = 1) -> bool:
        if not isinstance(cost, int):
            raise TypeError("cost must be an int")
        if cost < 0:
            raise ValueError("cost must be non-negative")

        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    def _refill(self) -> None:
        current = float(self._now())
        if current <= self._last_refill:
            return

        elapsed = current - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._last_refill = current
