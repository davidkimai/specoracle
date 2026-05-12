from __future__ import annotations

import math
import time
from collections.abc import Callable
from numbers import Real

__all__ = ["TokenBucketEnforcer"]


class TokenBucketEnforcer:
    """Token bucket rate enforcer.

    The bucket starts full. Each call to allow() refills tokens based on elapsed
    time, caps the balance at capacity, and spends the requested cost only when
    enough tokens are available.
    """

    __slots__ = ("capacity", "refill_rate", "_now", "_tokens", "_last_refill")

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Callable[[], float] | None = None,
    ) -> None:
        self.capacity = _validate_capacity(capacity)
        self.refill_rate = _validate_refill_rate(refill_rate)
        self._now = time.monotonic if now is None else _validate_now_callable(now)
        self._tokens = float(self.capacity)
        self._last_refill = self._read_time()

    def allow(self, cost: int = 1) -> bool:
        cost = _validate_cost(cost)
        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    def _refill(self) -> None:
        current_time = self._read_time()
        elapsed = current_time - self._last_refill

        if elapsed < 0:
            raise ValueError("now() must not move backwards")

        if elapsed == 0:
            return

        self._tokens = min(
            float(self.capacity),
            self._tokens + elapsed * self.refill_rate,
        )
        self._last_refill = current_time

    def _read_time(self) -> float:
        value = self._now()
        if not isinstance(value, Real) or isinstance(value, bool):
            raise TypeError("now() must return a real number")

        current_time = float(value)
        if not math.isfinite(current_time):
            raise ValueError("now() must return a finite number")

        return current_time


def _validate_capacity(capacity: int) -> int:
    if not isinstance(capacity, int) or isinstance(capacity, bool):
        raise TypeError("capacity must be an integer")

    if capacity < 0:
        raise ValueError("capacity must be non-negative")

    return capacity


def _validate_refill_rate(refill_rate: float) -> float:
    if not isinstance(refill_rate, Real) or isinstance(refill_rate, bool):
        raise TypeError("refill_rate must be a real number")

    value = float(refill_rate)
    if not math.isfinite(value):
        raise ValueError("refill_rate must be finite")

    if value < 0:
        raise ValueError("refill_rate must be non-negative")

    return value


def _validate_cost(cost: int) -> int:
    if not isinstance(cost, int) or isinstance(cost, bool):
        raise TypeError("cost must be an integer")

    if cost < 0:
        raise ValueError("cost must be non-negative")

    return cost


def _validate_now_callable(now: Callable[[], float]) -> Callable[[], float]:
    if not callable(now):
        raise TypeError("now must be callable")

    return now
