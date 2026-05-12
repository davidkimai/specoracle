import math
import time
from numbers import Real


class TokenBucketEnforcer:
    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        self._capacity = _validate_capacity(capacity)
        self._refill_rate = _validate_refill_rate(refill_rate)
        self._now = time.monotonic if now is None else _validate_now_callable(now)
        self._tokens = float(self._capacity)
        self._updated_at = _validate_time(self._now())

    def allow(self, cost: int = 1) -> bool:
        cost = _validate_cost(cost)
        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def refill_rate(self) -> float:
        return self._refill_rate

    @property
    def available_tokens(self) -> float:
        self._refill()
        return self._tokens

    def _refill(self) -> None:
        current_time = _validate_time(self._now())

        if current_time < self._updated_at:
            raise ValueError("now() must not move backwards")

        elapsed = current_time - self._updated_at
        self._updated_at = current_time

        if elapsed == 0 or self._tokens == self._capacity:
            return

        added_tokens = elapsed * self._refill_rate
        self._tokens = min(float(self._capacity), self._tokens + added_tokens)


def _validate_capacity(value: int) -> int:
    if type(value) is not int:
        raise TypeError("capacity must be an int")
    if value < 0:
        raise ValueError("capacity must be non-negative")
    return value


def _validate_refill_rate(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("refill_rate must be a real number")

    rate = float(value)
    if not math.isfinite(rate):
        raise ValueError("refill_rate must be finite")
    if rate < 0:
        raise ValueError("refill_rate must be non-negative")
    return rate


def _validate_now_callable(value):
    if not callable(value):
        raise TypeError("now must be callable")
    return value


def _validate_time(value) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("now() must return a real number")

    current_time = float(value)
    if not math.isfinite(current_time):
        raise ValueError("now() must return a finite number")
    return current_time


def _validate_cost(value: int) -> int:
    if type(value) is not int:
        raise TypeError("cost must be an int")
    if value < 0:
        raise ValueError("cost must be non-negative")
    return value


__all__ = ["TokenBucketEnforcer"]
