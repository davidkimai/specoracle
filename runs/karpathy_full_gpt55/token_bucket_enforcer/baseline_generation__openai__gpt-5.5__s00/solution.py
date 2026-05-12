import math
import threading
import time
from typing import Callable, Optional


class TokenBucketEnforcer:
    """A simple token-bucket rate enforcer.

    Tokens are refilled based on elapsed time and capped at the configured
    capacity. Calls to ``allow`` consume tokens only when enough are available.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        try:
            refill_rate_value = float(refill_rate)
        except (TypeError, ValueError) as exc:
            raise TypeError("refill_rate must be a finite non-negative number") from exc

        if not math.isfinite(refill_rate_value) or refill_rate_value < 0:
            raise ValueError("refill_rate must be a finite non-negative number")

        if now is None:
            now_func = time.monotonic
        elif callable(now):
            now_func = now
        else:
            raise TypeError("now must be callable")

        self.capacity = capacity
        self.refill_rate = refill_rate_value
        self._now = now_func
        self._tokens = float(capacity)
        self._last_refill = self._read_now()
        self._lock = threading.Lock()

    def allow(self, cost: int = 1) -> bool:
        if isinstance(cost, bool) or not isinstance(cost, int):
            raise TypeError("cost must be an integer")
        if cost < 0:
            raise ValueError("cost must be non-negative")

        with self._lock:
            self._refill_locked()

            if float(cost) > self._tokens:
                return False

            self._tokens -= float(cost)
            return True

    def _read_now(self) -> float:
        value = float(self._now())
        if not math.isfinite(value):
            raise ValueError("now() must return a finite number")
        return value

    def _refill_locked(self) -> None:
        current = self._read_now()

        if current <= self._last_refill:
            return

        elapsed = current - self._last_refill
        self._last_refill = current

        if self.refill_rate == 0:
            return

        self._tokens = min(float(self.capacity), self._tokens + elapsed * self.refill_rate)
