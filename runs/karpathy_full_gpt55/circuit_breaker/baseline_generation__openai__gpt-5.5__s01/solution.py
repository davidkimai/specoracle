import threading
import time
from typing import Any, Callable, Optional, Tuple

__all__ = ["CircuitBreaker"]


class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"

    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        if isinstance(failure_threshold, bool) or not isinstance(failure_threshold, int):
            raise TypeError("failure_threshold must be an integer")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than zero")

        try:
            recovery_timeout_value = float(recovery_timeout)
        except (TypeError, ValueError) as exc:
            raise TypeError("recovery_timeout must be a number") from exc

        if recovery_timeout_value < 0:
            raise ValueError("recovery_timeout must be non-negative")

        if now is None:
            now = time.monotonic
        elif not callable(now):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_value
        self._now: Callable[[], float] = now

        self._state = self.CLOSED
        self._failure_count = 0
        self._opened_at: Optional[float] = None

        self._generation = 0
        self._lock = threading.RLock()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    @property
    def opened_at(self) -> Optional[float]:
        with self._lock:
            return self._opened_at

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if not callable(func):
            raise TypeError("func must be callable")

        state_at_start, generation = self._acquire_permission()

        try:
            result = func(*args, **kwargs)
        except BaseException:
            self._record_failure(state_at_start, generation)
            raise

        self._record_success(state_at_start, generation)
        return result

    __call__ = call

    def _acquire_permission(self) -> Tuple[str, int]:
        with self._lock:
            if self._state == self.CLOSED:
                return self.CLOSED, self._generation

            if self._state == self.OPEN:
                current_time = self._now()
                opened_at = self._opened_at

                if opened_at is not None and current_time - opened_at >= self.recovery_timeout:
                    self._state = self.HALF_OPEN
                    self._generation += 1
                    return self.HALF_OPEN, self._generation

                raise RuntimeError("Circuit breaker is open")

            raise RuntimeError("Circuit breaker is half-open")

    def _record_success(self, state_at_start: str, generation: int) -> None:
        with self._lock:
            if state_at_start == self.HALF_OPEN:
                if self._state == self.HALF_OPEN and self._generation == generation:
                    self._close_locked()
                return

            if state_at_start == self.CLOSED:
                if self._state == self.CLOSED and self._generation == generation:
                    self._failure_count = 0

    def _record_failure(self, state_at_start: str, generation: int) -> None:
        with self._lock:
            if state_at_start == self.HALF_OPEN:
                if self._state == self.HALF_OPEN and self._generation == generation:
                    self._open_locked()
                return

            if state_at_start == self.CLOSED:
                if self._state == self.CLOSED and self._generation == generation:
                    self._failure_count += 1
                    if self._failure_count >= self.failure_threshold:
                        self._open_locked()

    def _open_locked(self) -> None:
        self._state = self.OPEN
        self._failure_count = self.failure_threshold
        self._opened_at = self._now()
        self._generation += 1

    def _close_locked(self) -> None:
        self._state = self.CLOSED
        self._failure_count = 0
        self._opened_at = None
        self._generation += 1
