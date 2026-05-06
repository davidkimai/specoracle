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
        return self._state.name

    def _transition_to(self, new_state: _State):
        self._state = new_state

    def update_thresholds(self, failure_threshold=None, recovery_timeout=None):
        if failure_threshold is not None:
            if failure_threshold <= 0:
                raise ValueError("failure_threshold must be positive")
            self.failure_threshold = failure_threshold
        if recovery_timeout is not None:
            if recovery_timeout <= 0:
                raise ValueError("recovery_timeout must be positive")
            self.recovery_timeout = recovery_timeout

    def call(self, func):
        if self._state == _State.OPEN:
            elapsed = self._now() - self._opened_at
            if elapsed >= self.recovery_timeout:
                self._transition_to(_State.HALF_OPEN)
            else:
                raise RuntimeError(
                    f"Circuit is open; retry after {self.recovery_timeout - elapsed:.3f}s"
                )

        if self._state == _State.HALF_OPEN:
            try:
                result = func()
            except Exception:
                self._opened_at = self._now()
                self._transition_to(_State.OPEN)
                raise
            else:
                self._failure_count = 0
                self._transition_to(_State.CLOSED)
                return result

        # CLOSED
        try:
            result = func()
        except Exception:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._opened_at = self._now()
                self._transition_to(_State.OPEN)
            raise
        else:
            self._failure_count = 0
            return result
