"""A state machine for managing retry logic."""

from __future__ import annotations


class RetryGate:
    """A simple state machine to manage retry logic.

    This class tracks consecutive failures and allows operations only when the
    failure count is below a specified maximum.
    """

    def __init__(self, max_attempts: int) -> None:
        """Initializes a RetryGate.

        Args:
            max_attempts: The maximum number of failures to allow before
                          disallowing further attempts. Must be a positive integer.

        Raises:
            TypeError: If max_attempts is not an integer.
            ValueError: If max_attempts is not positive.
        """
        if not isinstance(max_attempts, int):
            raise TypeError("max_attempts must be an integer.")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive.")

        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        """Checks if another attempt is permitted.

        Returns:
            True if the number of recorded failures is less than max_attempts,
            False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """Resets the failure count to zero, typically after a successful operation."""
        self._failure_count = 0

    def record_failure(self) -> None:
        """Increments the failure count by one."""
        self._failure_count += 1

    def remaining(self) -> int:
        """Calculates the number of remaining attempts.

        Returns:
            The number of attempts left before allow() returns False.
            This will be 0 if no attempts are remaining.
        """
        remaining_attempts = self._max_attempts - self._failure_count
        return max(0, remaining_attempts)
