import math
import threading
import time
from typing import Callable, Optional


class TokenBucketEnforcer:
    """
    Token-bucket rate enforcer.

    Args:
        capacity: Maximum number of tokens the bucket can hold. Must be a
            non-negative integer.
        refill_rate: Number of tokens added per second. Must be a finite,
            non-negative number.
        now: Optional callable returning the current time as a numeric value.
            Defaults to time.monotonic.

    The bucket starts full. Calls to allow() first refill the bucket based on
    elapsed time, capped at capacity, then consume tokens if enough are
    available.
    """

    __slots__ = ("_capacity", "_refill_rate", "_tokens", "_last_refill", "_now", "_lock")

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be non-negative")

        if isinstance(refill_rate, bool) or not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be a number")
        refill_rate_float = float(refill_rate)
        if not math.isfinite(refill_rate_float):
            raise ValueError("refill_rate must be finite")
        if refill_rate_float < 0:
            raise ValueError("refill_rate must be non-negative")

        if now is None:
            clock = time.monotonic
        elif callable(now):
            clock = now
        else:
            raise TypeError("now must be callable")

        initial_time = float(clock())
        if not math.isfinite(initial_time):
            raise ValueError("now() must return a finite number")

        self._capacity = capacity
        self._refill_rate = refill_rate_float
        self._tokens = float(capacity)
        self._last_refill = initial_time
        self._now = clock
        self._lock = threading.Lock()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def refill_rate(self) -> float:
        return self._refill_rate

    def allow(self, cost: int = 1) -> bool:
        if isinstance(cost, bool) or not isinstance(cost, int):
            raise TypeError("cost must be an integer")
        if cost < 0:
            raise ValueError("cost must be non-negative")

        with self._lock:
            self._refill_locked()

            if cost <= self._tokens:
                self._tokens -= float(cost)
                return True

            return False

    def _refill_locked(self) -> None:
        current_time = float(self._now())
        if not math.isfinite(current_time):
            raise ValueError("now() must return a finite number")

        elapsed = current_time - self._last_refill
        if elapsed <= 0:
            return

        self._last_refill = current_time

        if self._tokens >= self._capacity:
            self._tokens = float(self._capacity)
            return

        added = elapsed * self._refill_rate
        if added <= 0:
            return

        self._tokens = min(float(self._capacity), self._tokens + added)
