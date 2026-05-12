"""
A Circuit Breaker implementation adhering to Resilience Control Standard RCS-5.
"""

import enum
import time
from typing import Callable, Optional, TypeVar

# A generic type variable for the return value of the wrapped function.
_T = TypeVar("_T")


class State(enum.Enum):
    """
    Enumeration for the inspectable state of the circuit breaker, as required
    by RCS-5.
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


class CircuitBreaker:
    """
    An implementation of the Circuit Breaker pattern.

    The CircuitBreaker protects a function call from repeated failures.
    It starts in a CLOSED state, allowing calls to pass through. If the number
    of consecutive failures exceeds a threshold, it transitions to an OPEN
    state. In the OPEN state, all calls fail immediately with a RuntimeError
    without attempting to execute the function. After a recovery timeout, the
    circuit transitions to a HALF_OPEN state, allowing a single trial call.
    A successful trial closes the circuit; a failed trial re-opens it.
    """

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now: Optional[Callable[[], float]] = None,
    ):
        """
        Initializes the CircuitBreaker.

        Args:
            failure_threshold: A named configuration value for the number of
                consecutive failures required to open the circuit.
            recovery_timeout: A named configuration value for the time in
                seconds to wait in the OPEN state before transitioning to
                HALF_OPEN for a trial call.
            now: An optional callable that returns the current time in seconds.
                Defaults to time.monotonic. Used for testing.
        """
        if not isinstance(failure_threshold, int) or failure_threshold <= 0:
            raise ValueError("failure_threshold must be a positive integer")
        if not isinstance(recovery_timeout, (int, float)) or recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be a positive number")

        # Failure thresholds and recovery timers must be named configuration
        # values, not magic constants (RCS-5).
        self.failure_threshold: int = failure_threshold
        self.recovery_timeout: float = recovery_timeout
        self._now: Callable[[], float] = now if now is not None else time.monotonic

        # State transitions must be explicit and inspectable through a state
        # attribute (RCS-5).
        self.state: State = State.CLOSED
        self.failure_count: int = 0
        self._open_since: float = 0.0

    def call(self, func: Callable[[], _T]) -> _T:
        """
        Executes the given function, applying the circuit breaker logic.

        Args:
            func: The nullary function to execute.

        Returns:
            The return value of the function if it succeeds.

        Raises:
            RuntimeError: If the circuit is in the OPEN state and the recovery
                timeout has not elapsed.
            Any exception raised by the executed function.
        """
        if self.state is State.OPEN:
            if self._now() < self._open_since + self.recovery_timeout:
                raise RuntimeError("Circuit is open")
            # Recovery timeout has passed, transition to half-open for this trial.
            self.state = State.HALF_OPEN

        # At this point, state is either CLOSED or HALF_OPEN.
        # We attempt the call in both cases.
        try:
            result = func()
        except Exception:
            # The call failed.
            if self.state is State.HALF_OPEN:
                # Half-open trial failed. Re-open the circuit. (RCS-5)
                self._open_circuit()
            else:  # state is CLOSED
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    # Failure threshold reached. Open the circuit.
                    self._open_circuit()
            raise  # Re-raise the caught exception.

        # The call succeeded.
        if self.state is State.HALF_OPEN:
            # Half-open trial succeeded. Close the circuit. (RCS-5)
            self._close_circuit()
        elif self.failure_count > 0:
            # A successful call in CLOSED state resets the failure count.
            self.failure_count = 0

        return result

    def _open_circuit(self) -> None:
        """
        Performs the explicit state transition to OPEN.
        """
        self.state = State.OPEN
        self._open_since = self._now()

    def _close_circuit(self) -> None:
        """
        Performs the explicit state transition to CLOSED and resets counters.
        """
        self.state = State.CLOSED
        self.failure_count = 0
