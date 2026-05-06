"""
circuit_breaker.py

Implements a CircuitBreaker following Resilience Control Standard RCS-5:
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
    A circuit breaker that tracks failures and controls access to a protected
    function call.

    Parameters
    ----------
    failure_threshold : int
        Number of consecutive failures before the circuit opens.
    recovery_timeout : float
        Seconds to wait in the OPEN state before allowing a half-open trial.
    now : callable, optional
        A zero-argument callable returning the current time as a float
        (defaults to time.monotonic). Provided for testability.
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
        """Current state of the circuit breaker (inspectable per RCS-5)."""
        return self._state

    def update_thresholds(self, failure_threshold=None, recovery_timeout=None) -> None:
        """
        Replace active configuration values with the provided ones.

        Parameters
        ----------
        failure_threshold : int, optional
            New failure threshold; must be a positive integer if provided.
        recovery_timeout : float, optional
            New recovery timeout in seconds; must be positive if provided.

        Raises
        ------
        ValueError
            If a provided value is not positive.
        """
        if failure_threshold is not None:
            if failure_threshold <= 0:
                raise ValueError(
                    f"failure_threshold must be positive, got {failure_threshold!r}."
                )
            self.failure_threshold = failure_threshold

        if recovery_timeout is not None:
            if recovery_timeout <= 0:
                raise ValueError(
                    f"recovery_timeout must be positive, got {recovery_timeout!r}."
                )
            self.recovery_timeout = recovery_timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        """Perform an explicit, named state transition."""
        self._state = new_state

    def _record_failure(self) -> None:
        """Increment failure count and open the circuit if threshold is reached."""
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._opened_at = self._now()
            self._transition_to(CircuitState.OPEN)

    def _record_success(self) -> None:
        """Reset failure count and close the circuit."""
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
        Execute func if the circuit allows it.

        - CLOSED: execute normally; failures accumulate toward threshold.
        - OPEN: raise RuntimeError immediately (after checking for recovery).
        - HALF_OPEN: allow one trial; close on success, reopen on failure.

        Parameters
        ----------
        func : callable
            A zero-argument callable to protect.

        Returns
        -------
        The return value of func on success.

        Raises
        ------
        RuntimeError
            If the circuit is OPEN (and recovery timeout has not elapsed).
        Exception
            Any exception raised by func propagates after being recorded.
        """
        # Check whether recovery timeout has elapsed before deciding.
        self._check_recovery()

        if self._state is CircuitState.OPEN:
            raise RuntimeError(
                "Circuit is OPEN: calls are blocked until recovery timeout elapses."
            )

        if self._state is CircuitState.HALF_OPEN:
            return self._execute_half_open(func)

        # State is CLOSED.
        return self._execute_closed(func)

    def _execute_closed(self, func):
        """Execute func in the CLOSED state."""
        try:
            result = func()
            # A successful call in CLOSED state resets the failure counter.
            self._failure_count = 0
            return result
        except Exception:
            self._record_failure()
            raise

    def _execute_half_open(self, func):
        """
        Execute the single trial call in the HALF_OPEN state.
        Success closes the circuit; failure reopens it.
        """
        try:
            result = func()
            # Trial succeeded: close the circuit (RCS-5 half-open close-on-success).
            self._record_success()
            return result
        except Exception:
            # Trial failed: reopen the circuit (RCS-5 half-open reopen-on-failure).
            self._opened_at = self._now()
            self._failure_count = self.failure_threshold
            self._transition_to(CircuitState.OPEN)
            raise
