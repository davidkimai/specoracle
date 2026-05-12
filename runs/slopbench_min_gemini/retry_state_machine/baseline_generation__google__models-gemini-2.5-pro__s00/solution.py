"""
A module for implementing a simple stateful retry gate.
"""

from __future__ import annotations


class RetryGate:
    """
    A state machine to control retries based on a maximum number of attempts.

    The gate is initially open (`allow()` returns True). It closes after
    `max_attempts` failures have been recorded. A successful operation
    resets the failure count, reopening the gate.
    """

    def __init__(self, max_attempts: int):
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures to allow before the
                          gate closes. Must be a positive integer.

        Raises:
            ValueError: If max_attempts is not a positive integer.
        """
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        self._max_attempts: int = max_attempts
        self._failure_count: int = 0

    def allow(self) -> bool:
        """
        Checks if another attempt is allowed.

        Returns:
            True if the number of recorded failures is less than max_attempts,
            False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """
        Resets the failure count to zero, typically after a successful operation.
        """
        self._failure_count = 0

    def record_failure(self) -> None:
        """
        Increments the failure count by one.
        """
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts before the gate closes.

        Returns:
            The number of remaining attempts. This will be 0 if the gate
            is already closed.
        """
        remaining_count = self._max_attempts - self._failure_count
        return max(0, remaining_count)
