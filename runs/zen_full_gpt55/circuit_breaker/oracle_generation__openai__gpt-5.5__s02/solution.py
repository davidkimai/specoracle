import numbers
import threading
import time


class CircuitBreaker:
    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half-open"

    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        if isinstance(failure_threshold, bool) or not isinstance(failure_threshold, int):
            raise TypeError("failure_threshold must be an integer")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than zero")

        if isinstance(recovery_timeout, bool) or not isinstance(recovery_timeout, numbers.Real):
            raise TypeError("recovery_timeout must be a real number")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")

        if now is None:
            now = time.monotonic
        if not callable(now):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = float(recovery_timeout)
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.opened_at = None

        self._now = now
        self._lock = threading.Lock()
        self._half_open_trial_active = False

    def call(self, func, *args, **kwargs):
        if not callable(func):
            raise TypeError("func must be callable")

        trial_state = self._prepare_call()

        try:
            result = func(*args, **kwargs)
        except BaseException:
            self._record_failure(trial_state)
            raise

        self._record_success(trial_state)
        return result

    def _prepare_call(self):
        with self._lock:
            if self.state == self.STATE_OPEN:
                if self._recovery_timeout_elapsed(self._now()):
                    self._transition_to_half_open()
                else:
                    raise RuntimeError("circuit breaker is open")

            if self.state == self.STATE_HALF_OPEN:
                if self._half_open_trial_active:
                    raise RuntimeError("circuit breaker is half-open with an active trial")
                self._half_open_trial_active = True
                return self.STATE_HALF_OPEN

            if self.state == self.STATE_CLOSED:
                return self.STATE_CLOSED

            raise RuntimeError(f"circuit breaker has invalid state: {self.state!r}")

    def _record_success(self, trial_state):
        with self._lock:
            if trial_state == self.STATE_HALF_OPEN:
                self._transition_to_closed()
            elif trial_state == self.STATE_CLOSED and self.state == self.STATE_CLOSED:
                self.failure_count = 0

    def _record_failure(self, trial_state):
        with self._lock:
            if trial_state == self.STATE_HALF_OPEN:
                self._transition_to_open(self._now())
                return

            if trial_state == self.STATE_CLOSED and self.state == self.STATE_CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self._transition_to_open(self._now())

    def _recovery_timeout_elapsed(self, current_time):
        return (
            self.opened_at is not None
            and current_time - self.opened_at >= self.recovery_timeout
        )

    def _transition_to_closed(self):
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.opened_at = None
        self._half_open_trial_active = False

    def _transition_to_open(self, opened_at):
        self.state = self.STATE_OPEN
        self.failure_count = self.failure_threshold
        self.opened_at = opened_at
        self._half_open_trial_active = False

    def _transition_to_half_open(self):
        self.state = self.STATE_HALF_OPEN
        self._half_open_trial_active = False


__all__ = ["CircuitBreaker"]
