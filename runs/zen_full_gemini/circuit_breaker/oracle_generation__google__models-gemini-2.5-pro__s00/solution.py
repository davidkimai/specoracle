# -*- coding: utf-8 -*-
"""
A Circuit Breaker implementation compliant with Resilience Control Standard RCS-5.
"""

import enum
import time
from typing import Any, Callable, Optional, TypeVar

# Generic type variable for the return value of the wrapped function.
_T = TypeVar("_T")


class CircuitBreakerError(RuntimeError):
    """
    Raised when a call is made through a CircuitBreaker in the OPEN state.
    """
    pass


class State(enum.Enum):
    """
    Represents the state of the CircuitBreaker.

    As per RCS-5, state transitions are explicit and the state is inspectable.
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    An implementation of the Circuit Breaker pattern.

    The CircuitBreaker protects a function call from repeated failures.
    It has three states: CLOSED, OPEN, and HALF_OPEN.

    - CLOSED: The breaker is operating normally. Calls are passed through. If a
      call fails, the failure count is incremented. If the failure count
      exceeds the threshold, the breaker trips to the OPEN state.
    - OPEN: The breaker has tripped. Calls are not executed and immediately
      raise a CircuitBreakerError. After a recovery timeout, the breaker
      transitions to the HALF_OPEN state.
    - HALF_OPEN: The breaker allows a single trial call to pass through. If
      the call succeeds, the breaker resets to the CLOSED state. If it fails,
      the breaker returns to the OPEN state, and the recovery timer is reset.
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
            now: An optional callable that returns the current time in seconds.
                Used for testing. Defaults to time.monotonic.
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than 0")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be greater than 0")

        # --- Named configuration values as per RCS-5 ---
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self._now = now if now is not None else time.monotonic

        # --- State attributes as per RCS-5 ---
        self._state: State = State.CLOSED
        self._failure_count: int = 0
        self._last_failure_time: Optional[float] = None

    @property
    def state(self) -> State:
        """
        The current state of the circuit breaker. Explicitly inspectable as
        per RCS-5.

        Accessing this property may trigger a state transition from OPEN to
        HALF_OPEN if the recovery timeout has elapsed.
        """
        if self._state == State.OPEN:
            if self._last_failure_time is not None:
                elapsed = self._now() - self._last_failure_time
                if elapsed > self.recovery_timeout:
                    self._state = State.HALF_OPEN
        return self._state

    def _handle_success(self) -> None:
        """
        Handles a successful call, transitioning state as necessary.
        """
        if self._state == State.HALF_OPEN:
            # Half-open trial succeeded, close the circuit. (RCS-5)
            self._state = State.CLOSED
            self._failure_count = 0
            self._last_failure_time = None
        elif self._state == State.CLOSED:
            # Reset failure count on any success in the closed state.
            self._failure_count = 0
            self._last_failure_time = None

    def _handle_failure(self) -> None:
        """
        Handles a failed call, transitioning state as necessary.
        """
        if self._state == State.HALF_OPEN:
            # Half-open trial failed, re-open the circuit. (RCS-5)
            self._state = State.OPEN
            self._last_failure_time = self._now()
        elif self._state == State.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._state = State.OPEN
                self._last_failure_time = self._now()

    def call(self, func: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
        """
        Executes the given function according to the circuit breaker's state.

        Args:
            func: The callable to execute.
            *args: Positional arguments for func.
            **kwargs: Keyword arguments for func.

        Returns:
            The return value of func if it executes successfully.

        Raises:
            CircuitBreakerError: If the circuit is in the OPEN state.
            Exception: Any exception raised by func will be re-raised after
                the breaker's state is updated.
        """
        current_state = self.state

        if current_state == State.OPEN:
            raise CircuitBreakerError("Circuit is open")

        # If CLOSED or HALF_OPEN, attempt the call.
        try:
            result = func(*args, **kwargs)
        except Exception:
            self._handle_failure()
            raise

        self._handle_success()
        return result
