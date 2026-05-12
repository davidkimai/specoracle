import time
import threading


class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"

    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        if not isinstance(failure_threshold, int) or isinstance(failure_threshold, bool):
            raise TypeError("failure_threshold must be an integer")
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")

        clock = time.monotonic if now is None else now
        if not callable(clock):
            raise TypeError("now must be callable")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = float(recovery_timeout)
        self.state = self.CLOSED

        self.failure_count = 0
        self.opened_at = None

        self._now = clock
        self._lock = threading.RLock()
        self._half_open_trial_in_progress = False

    def call(self, func, *args, **kwargs):
        if not callable(func):
            raise TypeError("func must be callable")

        with self._lock:
            mode = self._prepare_call_locked()

        try:
            result = func(*args, **kwargs)
        except BaseException:
            with self._lock:
                self._record_failure_locked(mode)
            raise

        with self._lock:
            self._record_success_locked(mode)
        return result

    def _prepare_call_locked(self):
        if self.state == self.OPEN:
            if not self._recovery_timeout_elapsed_locked():
                raise RuntimeError("circuit breaker is open")
            self._move_to_half_open_locked()

        if self.state == self.HALF_OPEN:
            if self._half_open_trial_in_progress:
                raise RuntimeError("circuit breaker half-open trial already in progress")
            self._half_open_trial_in_progress = True
            return self.HALF_OPEN

        if self.state == self.CLOSED:
            return self.CLOSED

        raise RuntimeError(f"invalid circuit breaker state: {self.state!r}")

    def _record_success_locked(self, mode):
        if mode == self.HALF_OPEN:
            self._move_to_closed_locked()
        elif mode == self.CLOSED and self.state == self.CLOSED:
            self.failure_count = 0

    def _record_failure_locked(self, mode):
        if mode == self.HALF_OPEN:
            self._move_to_open_locked()
            return

        if mode == self.CLOSED and self.state == self.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._move_to_open_locked()

    def _recovery_timeout_elapsed_locked(self):
        if self.opened_at is None:
            return True
        return (self._now() - self.opened_at) >= self.recovery_timeout

    def _move_to_closed_locked(self):
        self.state = self.CLOSED
        self.failure_count = 0
        self.opened_at = None
        self._half_open_trial_in_progress = False

    def _move_to_open_locked(self):
        self.state = self.OPEN
        self.failure_count = self.failure_threshold
        self.opened_at = self._now()
        self._half_open_trial_in_progress = False

    def _move_to_half_open_locked(self):
        self.state = self.HALF_OPEN
        self._half_open_trial_in_progress = False
