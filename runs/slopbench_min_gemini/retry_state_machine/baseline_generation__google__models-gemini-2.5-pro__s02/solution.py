# No standard library imports are required for this module.

class RetryGate:
    """
    A state machine to manage retry attempts.

    This class provides a simple gate mechanism to control an operation that
    may fail and require retries. It counts failures and allows the operation
    to proceed as long as the failure count is below a specified maximum.
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
        Resets the failure count to zero.

        This should be called when the guarded operation succeeds.
        """
        self._failure_count = 0

    def record_failure(self) -> None:
        """
        Increments the failure count by one.

        This should be called when the guarded operation fails.
        """
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts.

        Returns:
            The number of attempts left before allow() returns False. This will
            be zero if the gate is already closed.
        """
        remaining_count = self._max_attempts - self._failure_count
        return max(0, remaining_count)
