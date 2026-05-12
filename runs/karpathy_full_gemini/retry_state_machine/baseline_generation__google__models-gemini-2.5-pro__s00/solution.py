"""
A module for implementing a simple retry state machine.
"""

import typing


class RetryGate:
    """
    A simple state machine to manage retries for an operation.

    This class tracks the number of consecutive failures and determines
    whether a new attempt should be allowed based on a maximum attempt limit.
    The state is entirely self-contained and deterministic.
    """

    _max_attempts: int
    _failure_count: int

    def __init__(self, max_attempts: int) -> None:
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures allowed before
                          disallowing further attempts. Must be a positive integer.

        Raises:
            ValueError: If max_attempts is not a positive integer.
        """
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer.")
        self._max_attempts = max_attempts
        self._failure_count = 0

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
        Calculates the number of remaining attempts.

        Returns:
            The number of attempts left before `allow()` returns False.
            This will be 0 if the gate is closed.
        """
        remaining_count = self._max_attempts - self._failure_count
        return max(0, remaining_count)
