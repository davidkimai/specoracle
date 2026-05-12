import time
from enum import Enum, auto
from typing import Callable, Any, Optional

__all__ = ["CircuitBreaker"]


class _State(Enum):
    """Enumeration for the state of the circuit breaker."""
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    """
    An implementation of the Circuit Breaker pattern.

    A circuit breaker is used to provide stability and prevent cascading failures
    in distributed systems. It wraps a function call and monitors it for failures.
    When the number of failures reaches a threshold, it "opens" the circuit,
    and subsequent calls will fail immediately without executing the function.
    After a timeout, the circuit transitions to a "half-open" state, allowing a
    single trial call. A success in this state closes the circuit, while a failure
    re-opens it.
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
                               open the circuit. Must be a positive integer.
            recovery_timeout: The time in seconds to wait in the OPEN state
                              before transitioning to HALF_OPEN. Must be a
                              non-negative number.
            now: An optional callable that returns the current time as a float
                 (e.g., time.time). This is primarily for testing purposes.
                 If None, time.time is used.
        """
        if not isinstance(failure_threshold, int) or failure_threshold <= 0:
            raise ValueError("failure_threshold must be a positive integer")
        if not isinstance(recovery_timeout, (int, float)) or recovery_timeout < 0:
            raise ValueError("recovery_timeout must be a non-negative number")

        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.time

        self._state = _State.CLOSED
        self._failure_count = 0
        self._opened_at: float = 0.0

    def call(self, func: Callable[[], Any]) -> Any:
        """
        Executes the given function according to the circuit breaker's state.

        Args:
            func: The callable to execute. It must not take any arguments.

        Returns:
            The result of the function call if it was successful.

        Raises:
            RuntimeError: If the circuit is in the OPEN state and the recovery
                          timeout has not yet passed.
            Any exception raised by the `func` itself is propagated after being
            recorded as a failure.
        """
        if self._state == _State.OPEN:
            if self._now() - self._opened_at >= self._recovery_timeout:
                self._state = _State.HALF_OPEN
            else:
                raise RuntimeError("Circuit is open.")

        # At this point, the state is either CLOSED or HALF_OPEN.
        # We can attempt to execute the function.
        try:
            result = func()
        except Exception:
            self._handle_failure()
            raise

        self._handle_success()
        return result

    def _handle_success(self) -> None:
        """Records a successful call and updates the state accordingly."""
        # A success in either CLOSED or HALF_OPEN state resets the circuit.
        self._state = _State.CLOSED
        self._failure_count = 0
        self._opened_at = 0.0

    def _handle_failure(self) -> None:
        """Records a failed call and updates the state accordingly."""
        if self._state == _State.HALF_OPEN:
            # A failure in the trial state immediately re-opens the circuit.
            self._trip()
        elif self._state == _State.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                self._trip()

    def _trip(self) -> None:
        """Transitions the circuit to the OPEN state."""
        self._state = _State.OPEN
        self._opened_at = self._now()
