import time
from typing import Callable, Optional, TypeVar


T = TypeVar("T")


class CircuitBreaker:
    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half-open"

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ):
        if not isinstance(failure_threshold, int) or isinstance(failure_threshold, bool):
            raise TypeError("failure_threshold must be an integer")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than zero")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")

        if now is None:
            now = time.monotonic
        if not callable(now):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = float(recovery_timeout)
        self.now = now

        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.opened_at = None

    def call(self, func: Callable[[], T]) -> T:
        if not callable(func):
            raise TypeError("func must be callable")

        if self.state == self.STATE_OPEN:
            if not self._recovery_timeout_elapsed():
                raise RuntimeError("circuit breaker is open")
            self._transition_to_half_open()

        if self.state == self.STATE_HALF_OPEN:
            return self._call_half_open(func)

        if self.state == self.STATE_CLOSED:
            return self._call_closed(func)

        raise RuntimeError(f"invalid circuit breaker state: {self.state!r}")

    def _call_closed(self, func: Callable[[], T]) -> T:
        try:
            result = func()
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
            raise
        else:
            self.failure_count = 0
            return result

    def _call_half_open(self, func: Callable[[], T]) -> T:
        try:
            result = func()
        except Exception:
            self._transition_to_open()
            raise
        else:
            self._transition_to_closed()
            return result

    def _recovery_timeout_elapsed(self) -> bool:
        if self.opened_at is None:
            return True
        return (self.now() - self.opened_at) >= self.recovery_timeout

    def _transition_to_closed(self) -> None:
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.opened_at = None

    def _transition_to_open(self) -> None:
        self.state = self.STATE_OPEN
        self.opened_at = self.now()

    def _transition_to_half_open(self) -> None:
        self.state = self.STATE_HALF_OPEN
        self.failure_count = 0
