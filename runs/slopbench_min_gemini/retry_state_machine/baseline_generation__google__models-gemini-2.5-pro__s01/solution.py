"""
A module to implement a state machine for retrying operations.
"""

class RetryGate:
    """
    A state machine that tracks failures and allows operations based on a retry limit.

    This class provides a simple mechanism to control retry logic by keeping track
    of consecutive failures.
    """

    def __init__(self, max_attempts: int):
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures allowed before the gate
                          closes. Must be a positive integer.

        Raises:
            ValueError: If max_attempts is not a positive integer.
        """
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        """
        Checks if further attempts are allowed.

        Returns:
            True if the number of recorded failures is less than max_attempts,
            False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """
        Resets the failure count to zero.

        This should be called after a successful operation to reset the retry
        counter.
        """
        self._failure_count = 0

    def record_failure(self) -> None:
        """
        Increments the failure count by one.

        This should be called after a failed operation.
        """
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts before the gate closes.

        Returns:
            The number of additional failures that can be recorded before allow()
            returns False. This will be 0 if the gate is already closed (i.e.,
            if allow() is False).
        """
        remaining_attempts = self._max_attempts - self._failure_count
        return max(0, remaining_attempts)
