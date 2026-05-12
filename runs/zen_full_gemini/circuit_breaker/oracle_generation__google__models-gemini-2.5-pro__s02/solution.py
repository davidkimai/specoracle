import enum
import time
from typing import Callable, Optional, TypeVar

__all__ = ["CircuitBreaker", "State"]

T = TypeVar("T")


class State(enum.Enum):
    """
    Enumeration for the state of the circuit breaker.

    RCS-5: State transitions must be explicit and inspectable.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent an application from
    repeatedly trying to execute an operation that is likely to fail.
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
            failure_threshold: The number of consecutive failures required to
                               open the circuit.
            recovery_timeout: The time in seconds to wait in the OPEN state
                              before transitioning to HALF_OPEN.
            now: An optional callable that returns the current time as a float
                 (e.g., seconds since the epoch), used for testing. Defaults
                 to time.monotonic.
        """
        if not isinstance(failure_threshold, int) or failure_threshold <= 0:
            raise ValueError("failure_threshold must be a positive integer")
        if not isinstance(recovery_timeout, (int, float)) or recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be a positive number")

        # RCS-5: Failure thresholds and recovery timers must be named
        # configuration values.
        self.failure_threshold: int = failure_threshold
        self.recovery_timeout: float = recovery_timeout

        # RCS-5: State must be inspectable through a state attribute.
        self.state: State = State.CLOSED

        self.failure_count: int = 0
        self.last_failure_time: Optional[float] = None
        self._now: Callable[[], float] = now if now is not None else time.monotonic

    def _trip(self) -> None:
        """Transitions the circuit to the OPEN state."""
        self.state = State.OPEN
        self.last_failure_time = self._now()

    def _reset(self) -> None:
        """Resets the circuit to the CLOSED state."""
        self.state = State.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def call(self, func: Callable[[], T]) -> T:
        """
        Executes the function `func` according to the circuit breaker's state.

        Args:
            func: The callable to be executed.

        Returns:
            The result of `func` if it is successful.

        Raises:
            RuntimeError: If the circuit is open and the recovery timeout has
                          not yet elapsed.
            Any exception raised by `func`.
        """
        if self.state == State.OPEN:
            if (
                self.last_failure_time is not None
                and (self._now() - self.last_failure_time) >= self.recovery_timeout
            ):
                self.state = State.HALF_OPEN
                # Fall-through to the HALF_OPEN state logic for a trial run.
            else:
                raise RuntimeError("Circuit is open")

        if self.state == State.HALF_OPEN:
            # The circuit is half-open, attempt one trial call.
            try:
                result = func()
            except Exception:
                # RCS-5: Half-open trial reopens on failure.
                self._trip()
                raise
            else:
                # RCS-5: Half-open trial closes on success.
                self._reset()
                return result

        if self.state == State.CLOSED:
            # The circuit is closed, execute the function normally.
            try:
                result = func()
            except Exception:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self._trip()
                raise
            else:
                # On success, reset the failure count.
                self.failure_count = 0
                return result

        # This code should be unreachable if the state machine logic is correct.
        # It's included as a defensive measure against unexpected states.
        raise RuntimeError(f"CircuitBreaker entered an invalid state: {self.state}")
