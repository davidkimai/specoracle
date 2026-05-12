import math
import threading
import time
from typing import Callable, Optional


class TokenBucketEnforcer:
    """
    Token bucket rate enforcer.

    Args:
        capacity: Maximum number of tokens the bucket can hold. The bucket starts full.
        refill_rate: Number of tokens added per second.
        now: Optional callable returning the current time as a numeric value. If omitted,
             time.monotonic is used.

    Methods:
        allow(cost=1): Refill based on elapsed time, then attempt to consume cost tokens.
    """

    def __init__(self, capacity: int, refill_rate: float, *, now: Optional[Callable[[], float]] = None):
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be non-negative")

        if isinstance(refill_rate, bool) or not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be a number")
        refill_rate = float(refill_rate)
        if not math.isfinite(refill_rate):
            raise ValueError("refill_rate must be finite")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")

        if now is None:
            now = time.monotonic
        elif not callable(now):
            raise TypeError("now must be callable")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self._now = now
        self._tokens = float(capacity)
        self._last_refill = self._read_time()
        self._lock = threading.Lock()

    def allow(self, cost: int = 1) -> bool:
        if isinstance(cost, bool) or not isinstance(cost, int):
            raise TypeError("cost must be an integer")
        if cost < 0:
            raise ValueError("cost must be non-negative")

        with self._lock:
            self._refill()

            if float(cost) > self._tokens:
                return False

            self._tokens -= float(cost)
            return True

    def _read_time(self) -> float:
        current = self._now()
        if isinstance(current, bool) or not isinstance(current, (int, float)):
            raise TypeError("now() must return a number")
        current = float(current)
        if not math.isfinite(current):
            raise ValueError("now() must return a finite number")
        return current

    def _refill(self) -> None:
        current = self._read_time()
        elapsed = current - self._last_refill

        if elapsed <= 0:
            return

        if self.refill_rate > 0 and self._tokens < self.capacity:
            self._tokens = min(float(self.capacity), self._tokens + elapsed * self.refill_rate)

        self._last_refill = current
