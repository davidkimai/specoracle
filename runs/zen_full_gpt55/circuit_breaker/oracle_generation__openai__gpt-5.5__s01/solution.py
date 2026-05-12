import time
from threading import Lock
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


class CircuitBreaker:
    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        if not isinstance(failure_threshold, int):
            raise TypeError("failure_threshold must be an int")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than zero")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = float(recovery_timeout)
        self.now = now if now is not None else time.monotonic

        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.opened_at = None

        self._lock = Lock()

    def call(self, func: Callable[[], T]) -> T:
        if not callable(func):
            raise TypeError("func must be callable")

        with self._lock:
            self._prepare_call_or_raise()

        try:
            result = func()
        except Exception:
            with self._lock:
                self._record_failure()
            raise

        with self._lock:
            self._record_success()

        return result

    def _prepare_call_or_raise(self) -> None:
        if self.state == self.STATE_CLOSED:
            return

        if self.state == self.STATE_OPEN:
            if self._recovery_timeout_elapsed():
                self._transition_to_half_open()
                return
            raise RuntimeError("circuit breaker is open")

        if self.state == self.STATE_HALF_OPEN:
            raise RuntimeError("circuit breaker is half-open; trial already in progress")

        raise RuntimeError(f"invalid circuit breaker state: {self.state!r}")

    def _record_success(self) -> None:
        if self.state == self.STATE_HALF_OPEN:
            self._transition_to_closed()
            return

        if self.state == self.STATE_CLOSED:
            self.failure_count = 0
            return

    def _record_failure(self) -> None:
        if self.state == self.STATE_HALF_OPEN:
            self._transition_to_open()
            return

        if self.state == self.STATE_CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
            return

        if self.state == self.STATE_OPEN:
            return

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
        self.failure_count = self.failure_threshold
        self.opened_at = self.now()

    def _transition_to_half_open(self) -> None:
        self.state = self.STATE_HALF_OPEN
        self.failure_count = 0
