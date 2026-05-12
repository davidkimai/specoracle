import time
import threading
from typing import Any, Callable, Optional


class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"

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
            raise ValueError("failure_threshold must be positive")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")
        if now is not None and not callable(now):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = float(recovery_timeout)
        self._now = now if now is not None else time.monotonic

        self._state = self.CLOSED
        self._failure_count = 0
        self._opened_at: Optional[float] = None
        self._half_open_trial_in_progress = False
        self._lock = threading.RLock()

    @property
    def state(self) -> str:
        with self._lock:
            self._maybe_transition_to_half_open()
            return self._state

    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if not callable(func):
            raise TypeError("func must be callable")

        with self._lock:
            self._before_call()

        try:
            result = func(*args, **kwargs)
        except BaseException:
            with self._lock:
                self._record_failure()
            raise

        with self._lock:
            self._record_success()
        return result

    def _before_call(self) -> None:
        self._maybe_transition_to_half_open()

        if self._state == self.OPEN:
            raise RuntimeError("circuit breaker is open")

        if self._state == self.HALF_OPEN:
            if self._half_open_trial_in_progress:
                raise RuntimeError("circuit breaker is half-open; trial already in progress")
            self._half_open_trial_in_progress = True

    def _record_success(self) -> None:
        if self._state == self.HALF_OPEN:
            self._half_open_trial_in_progress = False

        self._state = self.CLOSED
        self._failure_count = 0
        self._opened_at = None

    def _record_failure(self) -> None:
        if self._state == self.HALF_OPEN:
            self._half_open_trial_in_progress = False
            self._open()
            return

        if self._state == self.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._open()

    def _open(self) -> None:
        self._state = self.OPEN
        self._opened_at = self._now()
        self._half_open_trial_in_progress = False
        self._failure_count = self.failure_threshold

    def _maybe_transition_to_half_open(self) -> None:
        if self._state != self.OPEN:
            return

        if self._opened_at is None:
            return

        if self._now() - self._opened_at >= self.recovery_timeout:
            self._state = self.HALF_OPEN
            self._half_open_trial_in_progress = False
