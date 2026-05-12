#
# Copyright (c) 2024, SynthAI Secure Program Synthesis.
#
# All rights reserved.
#
# This software is the confidential and proprietary information of
# SynthAI ("Confidential Information"). You shall not disclose such
# Confidential Information and shall use it only in accordance with
# the terms of the license agreement you entered into with SynthAI.
#
"""
A module for implementing the Circuit Breaker resilience pattern.

This module provides a CircuitBreaker class that conforms to the Resilience
Control Standard RCS-5 for explicit state management and configuration.
"""

from __future__ import annotations

import time
from typing import Callable, Final, TypeVar, final

# Generic type variable for the return value of the wrapped function.
R = TypeVar("R")


@final
class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent repeated calls to a
    service that is likely to be unavailable.

    A circuit breaker can be in one of three states:
    - CLOSED: Normal operation. Calls are passed through to the function.
              Failures are counted.
    - OPEN: The circuit has tripped. Calls fail immediately without
            attempting to execute the function. After a timeout, the
            circuit transitions to HALF_OPEN.
    - HALF_OPEN: A single trial call is allowed. If it succeeds, the
                 circuit transitions to CLOSED. If it fails, it
                 transitions back to OPEN.
    """

    # State constants as per RCS-5 for inspectability.
    STATE_CLOSED: Final[str] = "closed"
    STATE_OPEN: Final[str] = "open"
    STATE_HALF_OPEN: Final[str] = "half_open"

    # Public state attribute as per RCS-5.
    state: str

    _failure_threshold: int
    _recovery_timeout: float

    _failure_count: int
    _opened_at: float
    _now: Callable[[], float]

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        now: Callable[[], float] | None = None,
    ):
        """
        Initializes the CircuitBreaker.

        Args:
            failure_threshold: The number of consecutive failures required to
                               open the circuit. Must be a positive integer.
            recovery_timeout: The time in seconds to wait in the OPEN state
                              before allowing a trial call (HALF_OPEN).
                              Must be a positive float.
            now: An optional callable that returns the current time in seconds.
                 Defaults to time.monotonic. Used for testing.
        """
        if not isinstance(failure_threshold, int) or failure_threshold <= 0:
            raise ValueError("failure_threshold must be a positive integer")
        if not isinstance(recovery_timeout, (int, float)) or recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be a positive number")

        # Configuration values as per RCS-5.
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout

        self._now = now if now is not None else time.monotonic

        self.state = self.STATE_CLOSED
        self._failure_count = 0
        self._opened_at = 0.0

    def call(self, func: Callable[[], R]) -> R:
        """
        Executes the given function if the circuit is closed or half-open.

        Args:
            func: The callable to execute.

        Returns:
            The result of the function call.

        Raises:
            RuntimeError: If the circuit is open and the recovery timeout has
                          not yet passed.
            Exception: The original exception from `func` if it fails.
        """
        if self.state == self.STATE_OPEN:
            if self._is_recovery_timeout_elapsed():
                self._transition_to_half_open()
            else:
                raise RuntimeError("Circuit is open")

        # In CLOSED or HALF_OPEN state, attempt the call.
        try:
            result = func()
        except Exception:
            self._handle_failure()
            raise
        else:
            self._handle_success()
            return result

    def _is_recovery_timeout_elapsed(self) -> bool:
        """Checks if the recovery timeout has passed since the circuit opened."""
        return self._now() - self._opened_at >= self._recovery_timeout

    def _handle_failure(self) -> None:
        """Handles the logic for a failed call based on the current state."""
        if self.state == self.STATE_HALF_OPEN:
            # Half-open trial failed, reopen the circuit.
            self._transition_to_open()
        else:  # state is CLOSED
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                self._transition_to_open()

    def _handle_success(self) -> None:
        """Handles the logic for a successful call based on the current state."""
        if self.state == self.STATE_HALF_OPEN:
            # Half-open trial succeeded, close the circuit.
            self._transition_to_closed()
        elif self.state == self.STATE_CLOSED:
            # Reset failure count on success.
            self._reset_failures()

    def _transition_to_open(self) -> None:
        """Transitions the circuit to the OPEN state."""
        self.state = self.STATE_OPEN
        self._opened_at = self._now()
        # Failure count is implicitly irrelevant in OPEN state.

    def _transition_to_half_open(self) -> None:
        """Transitions the circuit to the HALF_OPEN state."""
        self.state = self.STATE_HALF_OPEN

    def _transition_to_closed(self) -> None:
        """Transitions the circuit to the CLOSED state and resets failures."""
        self.state = self.STATE_CLOSED
        self._reset_failures()

    def _reset_failures(self) -> None:
        """Resets the failure counter."""
        self._failure_count = 0
