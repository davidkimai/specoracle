import time
import threading
from enum import Enum, auto
from typing import Callable, TypeVar, Optional, Any

# Generic type variable for the return value of the wrapped function.
ResultT = TypeVar("ResultT")


class CircuitBreakerState(Enum):
    """Enumeration for the state of the circuit breaker."""
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    """
    Implements a circuit breaker pattern to prevent repeated calls to a failing service.

    The circuit breaker has three states:
    - CLOSED: Initial state. Calls are executed. Failures are counted.
    - OPEN: After a threshold of failures, the circuit opens. Calls fail fast
            with a RuntimeError without being executed.
    - HALF_OPEN: After a recovery timeout, the circuit allows a single trial call.
                 If it succeeds, the circuit closes. If it fails, it re-opens.

    This implementation is thread-safe.
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
            recovery_timeout: The time in seconds the circuit will stay open
                              before allowing a trial call (half-open state).
                              Must be a non-negative number.
            now: An optional callable that returns the current time in seconds.
                 If None, `time.monotonic` is used. This is useful for testing.
        """
        if not isinstance(failure_threshold, int) or failure_threshold <= 0:
            raise ValueError("failure_threshold must be a positive integer")
        if not isinstance(recovery_timeout, (int, float)) or recovery_timeout < 0:
            raise ValueError("recovery_timeout must be a non-negative number")

        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.monotonic

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.RLock()

    @property
    def state(self) -> CircuitBreakerState:
        """Gets the current state of the circuit breaker.

        This property handles the automatic transition from OPEN to HALF_OPEN
        when the recovery timeout has expired.
        """
        with self._lock:
            if self._state == CircuitBreakerState.OPEN:
                if (
                    self._last_failure_time is not None
                    and self._now() - self._last_failure_time >= self._recovery_timeout
                ):
                    self._state = CircuitBreakerState.HALF_OPEN
            return self._state

    def call(self, func: Callable[[], ResultT]) -> ResultT:
        """
        Executes the given function if the circuit is closed or half-open.

        Args:
            func: The callable to execute.

        Returns:
            The result of the function call.

        Raises:
            RuntimeError: If the circuit is open and the recovery timeout has
                          not yet elapsed.
            Any exception raised by `func` is propagated.
        """
        with self._lock:
            # The `state` property access handles the OPEN -> HALF_OPEN transition.
            current_state = self.state

            if current_state == CircuitBreakerState.OPEN:
                raise RuntimeError("Circuit is open")

            # If CLOSED or HALF_OPEN, attempt the call.
            try:
                result = func()
            except Exception:
                self._handle_failure()
                raise  # Re-raise the original exception
            else:
                self._handle_success()
                return result

    def _handle_success(self) -> None:
        """Resets the circuit breaker to the CLOSED state on a successful call."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None

    def _handle_failure(self) -> None:
        """
        Handles a failed call, incrementing the failure count and potentially
        opening the circuit.
        """
        self._failure_count += 1
        if (
            self._state == CircuitBreakerState.HALF_OPEN
            or self._failure_count >= self._failure_threshold
        ):
            self._state = CircuitBreakerState.OPEN
            self._last_failure_time = self._now()

    def __repr__(self) -> str:
        """Provides a string representation of the circuit breaker's state."""
        return (
            f"{self.__class__.__name__}("
            f"failure_threshold={self._failure_threshold}, "
            f"recovery_timeout={self._recovery_timeout}, "
            f"state={self.state.name}, "
            f"failures={self._failure_count}"
            ")"
        )
