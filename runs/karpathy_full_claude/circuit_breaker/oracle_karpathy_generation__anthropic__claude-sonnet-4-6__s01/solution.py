"""
circuit_breaker.py

Implements CircuitBreaker following Resilience Control Standard RCS-5:
- State transitions are explicit and inspectable through a `state` attribute.
- Failure thresholds and recovery timers are named configuration values.
- Half-open trials either close on success or reopen on failure.
"""

import time as _time


class CircuitBreaker:
    """
    A circuit breaker with three states: CLOSED, OPEN, HALF_OPEN.

    Parameters
    ----------
    failure_threshold : int
        Number of consecutive failures required to open the circuit.
    recovery_timeout : float
        Seconds to wait in OPEN state before allowing a half-open trial.
    now : callable, optional
        Callable returning current time in seconds (defaults to time.monotonic).
        Useful for testing.
    """

    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._now = now if now is not None else _time.monotonic

        self._state = self.STATE_CLOSED
        self._failure_count = 0
        self._opened_at = None

    @property
    def state(self) -> str:
        """Current state of the circuit breaker (inspectable per RCS-5)."""
        return self._state

    def _transition_to(self, new_state: str) -> None:
        self._state = new_state

    def _check_recovery(self) -> None:
        """
        If the circuit is OPEN and the recovery timeout has elapsed,
        transition to HALF_OPEN to allow a single trial call.
        """
        if self._state == self.STATE_OPEN:
            elapsed = self._now() - self._opened_at
            if elapsed >= self.recovery_timeout:
                self._transition_to(self.STATE_HALF_OPEN)

    def call(self, func):
        """
        Execute *func* according to the current circuit state.

        - CLOSED: execute normally; count failures toward the threshold.
        - OPEN: raise RuntimeError immediately (after checking recovery timeout).
        - HALF_OPEN: allow one trial; close on success, reopen on failure.

        Returns the return value of *func* on success.
        Raises RuntimeError when the circuit is open.
        Re-raises any exception raised by *func*.
        """
        self._check_recovery()

        if self._state == self.STATE_OPEN:
            raise RuntimeError(
                "Circuit is open; calls are blocked until recovery timeout elapses."
            )

        if self._state == self.STATE_HALF_OPEN:
            return self._attempt_half_open(func)

        # STATE_CLOSED
        return self._attempt_closed(func)

    def _attempt_closed(self, func):
        try:
            result = func()
        except Exception:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._opened_at = self._now()
                self._transition_to(self.STATE_OPEN)
            raise
        else:
            # Success resets the failure counter.
            self._failure_count = 0
            return result

    def _attempt_half_open(self, func):
        try:
            result = func()
        except Exception:
            # Trial failed: reopen the circuit and reset the recovery clock.
            self._opened_at = self._now()
            self._transition_to(self.STATE_OPEN)
            raise
        else:
            # Trial succeeded: close the circuit and clear failure state.
            self._failure_count = 0
            self._opened_at = None
            self._transition_to(self.STATE_CLOSED)
            return result
