"""
circuit_breaker.py

Implements a Circuit Breaker following Resilience Control Standard RCS-5:
- State transitions are explicit and inspectable through a `state` attribute.
- Failure thresholds and recovery timers are named configuration values.
- Half-open trials either close on success or reopen on failure.
"""

import time
from enum import Enum, auto


class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    """
    A circuit breaker that wraps callables and trips after a configurable
    number of failures, recovering after a configurable timeout.

    Parameters
    ----------
    failure_threshold : int
        Number of consecutive failures before the circuit opens.
    recovery_timeout : float
        Seconds to wait in OPEN state before allowing a half-open trial.
    now : callable, optional
        Zero-argument callable returning the current time as a float
        (seconds). Defaults to time.monotonic. Useful for testing.
    """

    def __init__(self, failure_threshold: int, recovery_timeout: float, *, now=None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.monotonic

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None

    @property
    def state(self) -> CircuitState:
        """The current circuit state (CLOSED, OPEN, or HALF_OPEN)."""
        return self._state

    def update_thresholds(self, failure_threshold=None, recovery_timeout=None) -> None:
        """
        Replace active configuration values with new ones.

        Parameters
        ----------
        failure_threshold : int, optional
            New failure threshold. Must be a positive integer if provided.
        recovery_timeout : float, optional
            New recovery timeout in seconds. Must be positive if provided.

        Raises
        ------
        ValueError
            If any provided value is not positive.
        """
        if failure_threshold is not None:
            if failure_threshold <= 0:
                raise ValueError(
                    f"failure_threshold must be positive, got {failure_threshold!r}"
                )
            self.failure_threshold = failure_threshold

        if recovery_timeout is not None:
            if recovery_timeout <= 0:
                raise ValueError(
                    f"recovery_timeout must be positive, got {recovery_timeout!r}"
                )
            self.recovery_timeout = recovery_timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        self._state = new_state

    def _record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._opened_at = self._now()
            self._transition_to(CircuitState.OPEN)

    def _record_success(self) -> None:
        self._failure_count = 0
        self._opened_at = None
        self._transition_to(CircuitState.CLOSED)

    def _check_recovery(self) -> None:
        """
        If the circuit is OPEN and the recovery timeout has elapsed,
        transition to HALF_OPEN to allow a single trial call.
        """
        if self._state is CircuitState.OPEN:
            elapsed = self._now() - self._opened_at
            if elapsed >= self.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)

    def call(self, func):
        """
        Execute *func* according to the current circuit state.

        - CLOSED: execute normally; failures are counted.
        - OPEN: raise RuntimeError immediately (after checking for timeout).
        - HALF_OPEN: execute as a trial; success closes the circuit,
          failure reopens it.

        Returns the return value of *func* on success.
        Raises RuntimeError if the circuit is OPEN.
        Re-raises any exception raised by *func* (after updating state).
        """
        self._check_recovery()

        if self._state is CircuitState.OPEN:
            raise RuntimeError(
                "Circuit is OPEN; calls are blocked until recovery timeout elapses."
            )

        try:
            result = func()
        except Exception:
            if self._state is CircuitState.HALF_OPEN:
                # Trial failed — reopen the circuit
                self._opened_at = self._now()
                self._transition_to(CircuitState.OPEN)
            else:
                # CLOSED — count the failure
                self._record_failure()
            raise

        # Success path
        if self._state is CircuitState.HALF_OPEN:
            self._record_success()
        else:
            # CLOSED — reset failure counter on success
            self._failure_count = 0

        return result
