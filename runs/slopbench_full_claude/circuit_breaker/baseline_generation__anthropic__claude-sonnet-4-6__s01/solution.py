"""
Circuit Breaker implementation.

States:
  CLOSED     – normal operation; failures are counted.
  OPEN       – fast-fail; raises RuntimeError immediately.
  HALF_OPEN  – one trial call allowed after recovery_timeout elapses.
"""

import time
from enum import Enum, auto


class _State(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    """
    Parameters
    ----------
    failure_threshold : int
        Number of consecutive failures before the breaker opens.
    recovery_timeout : float
        Seconds to wait in the OPEN state before allowing a trial call.
    now : callable, optional
        Zero-argument callable returning the current time as a float
        (defaults to ``time.monotonic``).  Useful for testing.
    """

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now=None,
    ):
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be >= 0")

        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.monotonic

        self._state = _State.CLOSED
        self._failure_count = 0
        self._opened_at: float | None = None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        """Return the current state name as a lower-case string."""
        self._maybe_transition_to_half_open()
        return self._state.name.lower()

    @property
    def failure_count(self) -> int:
        return self._failure_count

    # ------------------------------------------------------------------
    # Core method
    # ------------------------------------------------------------------

    def call(self, func):
        """
        Execute *func* (a zero-argument callable) subject to the circuit
        breaker policy.

        Returns the return value of *func* on success.
        Raises ``RuntimeError`` when the circuit is OPEN.
        Re-raises whatever exception *func* raises on failure (and
        updates the breaker state accordingly).
        """
        self._maybe_transition_to_half_open()

        if self._state is _State.OPEN:
            raise RuntimeError(
                "Circuit is OPEN; calls are blocked until recovery timeout elapses."
            )

        # CLOSED or HALF_OPEN – attempt the call
        try:
            result = func()
        except Exception:
            self._record_failure()
            raise
        else:
            self._record_success()
            return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _maybe_transition_to_half_open(self):
        """
        If we are OPEN and enough time has elapsed, move to HALF_OPEN
        so that the next call is treated as a trial.
        """
        if (
            self._state is _State.OPEN
            and self._opened_at is not None
            and (self._now() - self._opened_at) >= self._recovery_timeout
        ):
            self._state = _State.HALF_OPEN

    def _record_failure(self):
        if self._state is _State.HALF_OPEN:
            # Trial call failed – go straight back to OPEN
            self._opened_at = self._now()
            self._state = _State.OPEN
            # Keep failure count at threshold (it was already there)
        else:
            # CLOSED state
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                self._opened_at = self._now()
                self._state = _State.OPEN

    def _record_success(self):
        # Any successful call resets the breaker to CLOSED
        self._state = _State.CLOSED
        self._failure_count = 0
        self._opened_at = None
