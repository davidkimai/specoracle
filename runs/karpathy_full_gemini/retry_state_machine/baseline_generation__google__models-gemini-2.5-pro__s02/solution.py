# No imports needed for this module.

class RetryGate:
    """
    Implements a state machine to manage retries based on a maximum attempt count.

    This gate tracks consecutive failures. A success resets the failure count.
    The gate is "open" (allow() returns True) as long as the number of
    consecutive failures is less than the configured maximum.
    """
    _max_attempts: int
    _failure_count: int

    def __init__(self, max_attempts: int) -> None:
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
            True if the number of failures is less than max_attempts,
            False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """Resets the failure count to zero."""
        self._failure_count = 0

    def record_failure(self) -> None:
        """Increments the failure count by one."""
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts.

        Returns:
            The number of attempts left before allow() returns False. This
            will be zero if the gate is closed.
        """
        return max(0, self._max_attempts - self._failure_count)
