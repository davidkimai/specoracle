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

    def call(self, func):
        if self._state == _State.OPEN:
            elapsed = self._now() - self._opened_at
            if elapsed >= self.recovery_timeout:
                self._transition_to(_State.HALF_OPEN)
            else:
                raise RuntimeError(
                    f"Circuit is open. Retry after {self.recovery_timeout - elapsed:.2f}s."
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

        # CLOSED state
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
