"""A state machine for managing retries."""


class RetryGate:
    """
    Manages retry logic based on a maximum number of attempts.

    This class provides a simple state machine to track consecutive failures and
    determine if a subsequent attempt should be allowed. The failure count is
    reset upon success.
    """

    def __init__(self, max_attempts: int):
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of consecutive failures allowed.
                          Must be a positive integer.

        Raises:
            ValueError: If max_attempts is not a positive integer.
        """
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer.")
        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        """
        Checks if another attempt is permitted.

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
        """
        Calculates the number of remaining attempts.

        Returns:
            The number of additional failures that can be recorded before
            `allow()` returns False. This will be zero if the gate is closed.
        """
        remaining_count = self._max_attempts - self._failure_count
        return max(0, remaining_count)
