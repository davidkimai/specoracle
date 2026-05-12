# circuit_breaker.py
"""
A Python implementation of the Circuit Breaker pattern.

This module provides a CircuitBreaker class that can be used to wrap function
calls to external services, preventing cascading failures when a service is
unresponsive.
"""

import enum
import time
from typing import Any, Callable, Optional, TypeVar

# --- Resilience Control Standard RCS-5 Compliance ---
# - State transitions are explicit via `_transition_to_*` methods and
#   inspectable through the `state` attribute.
# - `failure_threshold` and `recovery_timeout` are named configuration values
#   stored as instance attributes.
# - The `HALF_OPEN` state logic ensures trials either close the circuit on
#   success or re-open it on failure.

ResultType = TypeVar("ResultType")
CallableType = Callable[..., ResultType]


class State(enum.Enum):
    """Enumeration for the state of the circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(RuntimeError):
    """
    Exception raised when a call is made while the circuit is open and the
    recovery timeout has not yet elapsed.
    """


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to add resilience to function calls.

    A circuit breaker can be in one of three states: CLOSED, OPEN, or
    HALF_OPEN.

    - In the CLOSED state, calls are executed normally. If a call fails, a
      failure counter is incremented. If the counter exceeds the threshold,
      the circuit transitions to the OPEN state.
    - In the OPEN state, calls fail immediately with a CircuitBreakerOpenError
      without being executed. After a recovery timeout, the circuit
      transitions to the HALF_OPEN state.
    - In the HALF_OPEN state, one trial call is allowed. If it succeeds, the
      circuit transitions back to CLOSED. If it fails, it transitions back
      to OPEN.
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
            failure_threshold: The number of consecutive failures needed to
                open the circuit.
            recovery_timeout: The time in seconds to wait in the OPEN state
                before allowing a trial call (HALF_OPEN).
            now: An optional callable that returns the current time in seconds.
                Defaults to `time.monotonic`. Used for testing.
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be positive")

        # Configuration values (RCS-5)
        self.failure_threshold: int = failure_threshold
        self.recovery_timeout: float = recovery_timeout

        # State attribute (RCS-5)
        self.state: State = State.CLOSED

        self.failure_count: int = 0
        self.opened_at: float = 0.0

        self._now: Callable[[], float] = now if now is not None else time.monotonic

    def _transition_to_closed(self) -> None:
        """Explicitly transitions the circuit to the CLOSED state."""
        self.state = State.CLOSED
        self.failure_count = 0

    def _transition_to_open(self) -> None:
        """Explicitly transitions the circuit to the OPEN state."""
        self.state = State.OPEN
        self.opened_at = self._now()

    def _transition_to_half_open(self) -> None:
        """Explicitly transitions the circuit to the HALF_OPEN state."""
        self.state = State.HALF_OPEN

    def _on_success(self) -> None:
        """Handles the logic for a successful call."""
        if self.state == State.HALF_OPEN:
            # Half-open trial succeeded, close the circuit (RCS-5)
            self._transition_to_closed()
        elif self.state == State.CLOSED:
            # Reset failure count on success in closed state
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handles the logic for a failed call."""
        if self.state == State.HALF_OPEN:
            # Half-open trial failed, re-open the circuit (RCS-5)
            self._transition_to_open()
        elif self.state == State.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()

    def call(
        self, func: CallableType[ResultType], *args: Any, **kwargs: Any
    ) -> ResultType:
        """
        Executes the function `func` according to the circuit breaker's state.

        Args:
            func: The function to execute.
            *args: Positional arguments for `func`.
            **kwargs: Keyword arguments for `func`.

        Returns:
            The return value of `func` if it executes successfully.

        Raises:
            CircuitBreakerOpenError: If the circuit is in the OPEN state and the
                recovery timeout has not yet elapsed. This is a subclass of
                `RuntimeError` as specified.
            Exception: The original exception from `func` if it fails.
        """
        if self.state == State.OPEN:
            elapsed_time = self._now() - self.opened_at
            if elapsed_time >= self.recovery_timeout:
                self._transition_to_half_open()
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit is open. Time until next trial: "
                    f"{self.recovery_timeout - elapsed_time:.2f}s"
                )

        # In CLOSED or HALF_OPEN state, we attempt the call.
        try:
            result = func(*args, **kwargs)
        except Exception:
            self._on_failure()
            raise  # Re-raise the original exception to the caller.

        self._on_success()
        return result
