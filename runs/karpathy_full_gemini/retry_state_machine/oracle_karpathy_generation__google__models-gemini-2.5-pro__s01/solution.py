# retry_state_machine.py

"""
A module providing a simple, deterministic state machine for managing retry logic.
"""

from __future__ import annotations


class RetryGate:
    """
    A state machine to track and manage the number of allowed retry attempts.

    This class provides a simple gate that is "open" (allowing an operation)
    as long as the number of recorded failures has not reached a specified
    maximum. It is a deterministic, in-memory component with no side effects
    like I/O or threading.
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
        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        """
        Checks if another attempt is permitted.

        Returns:
            True if the number of recorded failures is less than max_attempts,
            False otherwise.
        """
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        """
        Resets the failure count to zero.

        This should be called after a successful operation to reset the retry
        state.
        """
        self._failures = 0

    def record_failure(self) -> None:
        """
        Increments the failure count by one.

        This should be called after a failed operation.
        """
        self._failures += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts before the gate closes.

        Returns:
            The number of attempts remaining. This will be 0 if the gate is
            closed.
        """
        return max(0, self._max_attempts - self._failures)
