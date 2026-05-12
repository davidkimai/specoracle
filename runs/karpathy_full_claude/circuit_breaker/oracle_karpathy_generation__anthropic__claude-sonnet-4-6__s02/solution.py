import time
from enum import Enum, auto


class _State(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.monotonic

        self._state = _State.CLOSED
        self._failure_count = 0
        self._opened_at = None

    @property
    def state(self):
        self._evaluate_state()
        return self._state

    def _evaluate_state(self):
        if self._state == _State.OPEN:
            elapsed = self._now() - self._opened_at
            if elapsed >= self.recovery_timeout:
                self._state = _State.HALF_OPEN

    def call(self, func):
        self._evaluate_state()

        if self._state == _State.OPEN:
            raise RuntimeError(
                "Circuit breaker is open; calls are blocked until recovery timeout elapses."
            )

        try:
            result = func()
        except Exception:
            self._on_failure()
            raise
        else:
            self._on_success()
            return result

    def _on_success(self):
        if self._state == _State.HALF_OPEN:
            self._state = _State.CLOSED
            self._failure_count = 0
            self._opened_at = None
        elif self._state == _State.CLOSED:
            self._failure_count = 0

    def _on_failure(self):
        if self._state == _State.HALF_OPEN:
            self._state = _State.OPEN
            self._opened_at = self._now()
        elif self._state == _State.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._state = _State.OPEN
                self._opened_at = self._now()
