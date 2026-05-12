# -*- coding: utf-8 -*-
"""
A thread-safe implementation of the Circuit Breaker pattern.
"""

import time
import threading
from enum import Enum, auto
from typing import Callable, TypeVar, Optional, Any

__all__ = ["CircuitBreaker"]

# Generic TypeVar for the return value of the function passed to call()
T = TypeVar("T")


class _State(Enum):
    """Enumeration for the internal state of the circuit breaker."""
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent repeated calls to a
    failing service. This implementation is thread-safe.

    A CircuitBreaker has three states:
    - CLOSED: The initial state. Calls are passed through to the wrapped function.
      If a call fails, a failure counter is incremented. If the counter exceeds a
      threshold, the state changes to OPEN.
    - OPEN: Calls immediately fail with a RuntimeError without executing the
      wrapped function. After a configured recovery timeout, the state changes to
      HALF_OPEN.
    - HALF-OPEN: The next call is allowed to pass through as a trial. If it
      succeeds, the state changes back to CLOSED. If it fails, the state
      returns to OPEN, and the recovery timeout is reset.
    """

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now: Optional[Callable[[], float]] = None
    ):
        """
        Initializes the CircuitBreaker.

        Args:
            failure_threshold: The number of consecutive failures required to
                open the circuit. Must be a positive integer.
            recovery_timeout: The number of seconds to wait in the OPEN state
                before transitioning to HALF-OPEN. Must be a non-negative float.
            now: An optional callable that returns the current time as a float
                (e.g., time.time). Used for dependency injection, primarily for
                testing. Defaults to time.time.

        Raises:
            ValueError: If failure_threshold or recovery_timeout are invalid.
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
        self._opened_at = 0.0
        self._lock = threading.RLock()

    @property
    def state(self) -> str:
        """Returns the current state of the circuit breaker as a string."""
        with self._lock:
            return self._state.name

    def _on_success(self) -> None:
        """
        Handles a successful call. This method must be called under a lock.
        """
        if self._state == _State.HALF_OPEN:
            self._state = _State.CLOSED
        self._failure_count = 0

    def _on_failure(self) -> None:
        """
        Handles a failed call. This method must be called under a lock.
        """
        if self._state == _State.HALF_OPEN:
            self._state = _State.OPEN
            self._opened_at = self._now()
        elif self._state == _State.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                self._state = _State.OPEN
                self._opened_at = self._now()

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Executes the given function if the circuit is not open.

        This method is thread-safe. It avoids holding a lock during the
        execution of `func` to prevent blocking other threads.

        Args:
            func: The callable to execute.
            *args: Positional arguments to pass to `func`.
            **kwargs: Keyword arguments to pass to `func`.

        Returns:
            The return value of the executed function.

        Raises:
            RuntimeError: If the circuit is in the OPEN state and the recovery
                          timeout has not yet elapsed.
            Any exception raised by the wrapped function `func`.
        """
        with self._lock:
            if self._state == _State.OPEN:
                elapsed_time = self._now() - self._opened_at
                if elapsed_time >= self._recovery_timeout:
                    self._state = _State.HALF_OPEN
                else:
                    raise RuntimeError("Circuit is open")

        # Execute the function outside the lock.
        # If the state transitioned from OPEN to HALF_OPEN, this call
        # serves as the trial run.
        try:
            result = func(*args, **kwargs)
        except Exception:
            with self._lock:
                self._on_failure()
            raise  # Re-raise the original exception

        with self._lock:
            self._on_success()

        return result
