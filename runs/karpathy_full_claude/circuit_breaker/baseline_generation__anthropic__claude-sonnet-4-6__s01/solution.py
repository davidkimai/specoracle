import time
from enum import Enum, auto


class _State(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.monotonic

        self._state = _State.CLOSED
        self._failure_count = 0
        self._opened_at = None

    @property
    def state(self):
        return self._state

    def _transition_to_open(self):
        self._state = _State.OPEN
        self._opened_at = self._now()

    def _check_recovery(self):
        if self._state == _State.OPEN:
            elapsed = self._now() - self._opened_at
            if elapsed >= self._recovery_timeout:
                self._state = _State.HALF_OPEN

    def call(self, func):
        self._check_recovery()

        if self._state == _State.OPEN:
            raise RuntimeError("Circuit breaker is open")

        try:
            result = func()
        except Exception:
            self._failure_count += 1
            if self._state == _State.HALF_OPEN:
                # Failed during half-open trial, go back to open
                self._transition_to_open()
            elif self._failure_count >= self._failure_threshold:
                self._transition_to_open()
            raise
        else:
            # Success
            if self._state == _State.HALF_OPEN:
                # Successful trial, reset to closed
                self._state = _State.CLOSED
                self._failure_count = 0
                self._opened_at = None
            else:
                # Successful call while closed, reset failure count
                self._failure_count = 0
            return result
