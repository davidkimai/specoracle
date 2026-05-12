import time
from typing import Any, Callable, Optional


STATE_CLOSED = "closed"
STATE_OPEN = "open"
STATE_HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        if not isinstance(failure_threshold, int):
            raise TypeError("failure_threshold must be an integer")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than zero")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.now = now if now is not None else time.monotonic

        self.state = STATE_CLOSED
        self.failure_count = 0
        self.opened_at: Optional[float] = None

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if not callable(func):
            raise TypeError("func must be callable")

        if self.state == STATE_OPEN:
            if self._recovery_timeout_elapsed():
                self._transition_to_half_open()
            else:
                raise RuntimeError("circuit breaker is open")

        if self.state == STATE_HALF_OPEN:
            return self._call_half_open_trial(func, *args, **kwargs)

        if self.state == STATE_CLOSED:
            return self._call_closed(func, *args, **kwargs)

        raise RuntimeError(f"invalid circuit breaker state: {self.state!r}")

    def _call_closed(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
            raise
        else:
            self.failure_count = 0
            return result

    def _call_half_open_trial(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        try:
            result = func(*args, **kwargs)
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
        self.state = STATE_CLOSED
        self.failure_count = 0
        self.opened_at = None

    def _transition_to_open(self) -> None:
        self.state = STATE_OPEN
        self.opened_at = self.now()

    def _transition_to_half_open(self) -> None:
        self.state = STATE_HALF_OPEN
        self.failure_count = 0
