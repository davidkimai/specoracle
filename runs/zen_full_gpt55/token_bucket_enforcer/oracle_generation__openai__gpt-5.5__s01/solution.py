import math
import time
from collections.abc import Callable
from typing import Optional


class TokenBucketEnforcer:
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        self.capacity = self._validate_capacity(capacity)
        self.refill_rate = self._validate_refill_rate(refill_rate)
        self._now = time.monotonic if now is None else self._validate_clock(now)

        self._tokens = float(self.capacity)
        self._last_refill = self._read_time()

    def allow(self, cost: int = 1) -> bool:
        cost = self._validate_cost(cost)
        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    @staticmethod
    def _validate_capacity(capacity: int) -> int:
        if type(capacity) is not int:
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        return capacity

    @staticmethod
    def _validate_refill_rate(refill_rate: float) -> float:
        if isinstance(refill_rate, bool) or not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be a finite number")
        refill_rate = float(refill_rate)
        if not math.isfinite(refill_rate):
            raise ValueError("refill_rate must be finite")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")
        return refill_rate

    @staticmethod
    def _validate_clock(now: Callable[[], float]) -> Callable[[], float]:
        if not callable(now):
            raise TypeError("now must be callable")
        return now

    @staticmethod
    def _validate_cost(cost: int) -> int:
        if type(cost) is not int:
            raise TypeError("cost must be an int")
        if cost < 0:
            raise ValueError("cost must be non-negative")
        return cost

    def _read_time(self) -> float:
        current_time = self._now()
        if isinstance(current_time, bool) or not isinstance(current_time, (int, float)):
            raise TypeError("now() must return a finite number")

        current_time = float(current_time)
        if not math.isfinite(current_time):
            raise ValueError("now() must return a finite number")
        return current_time

    def _refill(self) -> None:
        current_time = self._read_time()
        elapsed = current_time - self._last_refill

        if elapsed < 0:
            raise ValueError("now() must not move backwards")

        if elapsed == 0 or self._tokens == self.capacity:
            self._last_refill = current_time
            return

        self._tokens = min(
            float(self.capacity),
            self._tokens + elapsed * self.refill_rate,
        )
        self._last_refill = current_time
