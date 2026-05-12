#
# Copyright (c) 2024, Safe Synthesis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Resilience Control Standard RCS-5:
# - State transitions must be explicit and inspectable through a state attribute.
# - Failure thresholds and recovery timers must be named configuration values,
#   not magic constants.
# - Half-open trials must either close on success or reopen on failure.
#
"""
A circuit breaker implementation compliant with Resilience Control Standard RCS-5.
"""

import enum
import time
from typing import Callable, Optional, TypeVar

R = TypeVar("R")


class CircuitBreakerState(enum.Enum):
    """
    Enumeration for the explicit and inspectable state of the circuit breaker,
    as required by RCS-5.
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    An implementation of the Circuit Breaker pattern.

    The CircuitBreaker protects a system from repeated failures of a service.
    It wraps calls to the service and monitors for failures.

    - It starts in the CLOSED state, allowing calls to pass through.
    - If the number of consecutive failures exceeds a threshold, it trips
      and moves to the OPEN state.
    - In the OPEN state, all calls fail fast with a RuntimeError, preventing
      further calls to the failing service.
    - After a recovery timeout, it moves to the HALF_OPEN state, allowing a
      single trial call.
    - If the trial call succeeds, the breaker resets to the CLOSED state.
    - If the trial call fails, it returns to the OPEN state for another
      recovery timeout period.
    """

    # RCS-5: Named configuration values for thresholds and timers.
    failure_threshold: int
    recovery_timeout: float

    # RCS-5: Explicit and inspectable state attribute.
    state: CircuitBreakerState

    _failure_count: int
    _opened_at: Optional[float]
    _now: Callable[[], float]

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
                trip the circuit breaker. Must be a positive integer.
            recovery_timeout: The time in seconds to wait in the OPEN state
                before allowing a trial call in the HALF_OPEN state. Must be
                a positive number.
            now: An optional callable that returns the current time as a float.
                Defaults to time.monotonic. Used for testing.
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive.")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be positive.")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._now = now if now is not None else time.monotonic

        self._failure_count = 0
        self._opened_at = None
        self.state = CircuitBreakerState.CLOSED

    def _trip(self) -> None:
        """Transitions the circuit breaker to the OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self._opened_at = self._now()

    def _reset(self) -> None:
        """Resets the circuit breaker to the CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._opened_at = None

    def _on_closed_success(self) -> None:
        """Handles a successful call in the CLOSED state."""
        self._failure_count = 0

    def _on_closed_failure(self) -> None:
        """Handles a failed call in the CLOSED state."""
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._trip()

    def _is_recovery_timeout_elapsed(self) -> bool:
        """Checks if the recovery timeout has passed since the breaker opened."""
        if self._opened_at is None:
            return False
        return (self._now() - self._opened_at) >= self.recovery_timeout

    def call(self, func: Callable[[], R]) -> R:
        """
        Executes the function `func` according to the circuit breaker's state.

        Args:
            func: The callable to be executed.

        Returns:
            The return value of `func` if it executes successfully.

        Raises:
            RuntimeError: If the circuit breaker is in the OPEN state and the
                recovery timeout has not elapsed.
            Exception: Any exception raised by `func` is re-raised after being
                processed by the circuit breaker logic.
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._is_recovery_timeout_elapsed():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise RuntimeError("Circuit breaker is open")

        if self.state == CircuitBreakerState.CLOSED:
            try:
                result = func()
            except Exception:
                self._on_closed_failure()
                raise
            else:
                self._on_closed_success()
                return result

        if self.state == CircuitBreakerState.HALF_OPEN:
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

        # This code should be unreachable if the state machine is correct.
        # It serves as a safeguard against unexpected states.
        raise RuntimeError(f"CircuitBreaker in unexpected state: {self.state}")
