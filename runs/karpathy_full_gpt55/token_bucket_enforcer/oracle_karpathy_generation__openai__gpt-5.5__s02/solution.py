import time


class TokenBucketEnforcer:
    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self.capacity = capacity
        self.refill_rate = float(refill_rate)
        self._now = time.monotonic if now is None else now
        self._tokens = float(capacity)
        self._last_refill = float(self._now())

    def allow(self, cost: int = 1) -> bool:
        if not isinstance(cost, int):
            raise TypeError("cost must be an int")
        if cost < 0:
            raise ValueError("cost must be non-negative")

        current = float(self._now())
        elapsed = current - self._last_refill
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
            self._last_refill = current

        if cost <= self._tokens:
            self._tokens -= cost
            return True
        return False
