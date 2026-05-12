"""A state machine for managing retries."""

class RetryGate:
    """
    A simple state machine to track failures and control retries.

    This class provides a mechanism to allow a certain number of attempts for an
    operation, tracked by recorded failures. It can be reset upon success.
    """

    def __init__(self, max_attempts: int):
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures to allow before the
                          gate closes (i.e., allow() returns False).

        Raises:
            ValueError: If max_attempts is not positive.
        """
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
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
        """Resets the failure count to zero, typically after a successful operation."""
        self._failure_count = 0

    def record_failure(self) -> None:
        """Increments the failure count by one."""
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts.

        Returns:
            The number of attempts left before allow() will return False.
            This will be 0 if the failure count has reached or exceeded
            max_attempts.
        """
        return max(0, self._max_attempts - self._failure_count)
