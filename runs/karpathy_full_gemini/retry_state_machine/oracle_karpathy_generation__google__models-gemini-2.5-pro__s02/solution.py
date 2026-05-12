"""
A simple, deterministic state machine for managing retry logic.
"""

import sys

# Ensure compatibility with Python 3.8+ for typing
if sys.version_info < (3, 9):
    from typing import ClassVar
else:
    from typing import ClassVar


class RetryGate:
    """
    Manages state for a retry mechanism, tracking failures and successes.

    This class provides a simple gate-keeping mechanism to control whether an
    operation should be retried based on a configured maximum number of
    attempts. It is a deterministic state machine and does not involve time,
    I/O, or any external state.
    """

    _max_attempts: int
    _failure_count: int

    def __init__(self, max_attempts: int):
        """
        Initializes a RetryGate.

        Args:
            max_attempts: The maximum number of failures allowed before the gate
                          closes (i.e., `allow()` returns False). Must be a
                          positive integer.

        Raises:
            ValueError: If max_attempts is not a positive integer.
        """
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        """
        Checks if another attempt is permitted.

        An attempt is allowed if the current number of recorded failures is
        strictly less than the configured maximum attempts.

        Returns:
            True if the number of failures is less than max_attempts,
            False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """
        Records a successful attempt, resetting the failure count to zero.
        """
        self._failure_count = 0

    def record_failure(self) -> None:
        """
        Records a failed attempt, incrementing the failure count by one.
        """
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts before the gate closes.

        Returns:
            The number of attempts left before `allow()` returns False.
            This will be 0 if the failure count has reached or exceeded
            max_attempts.
        """
        remaining_count = self._max_attempts - self._failure_count
        return max(0, remaining_count)
