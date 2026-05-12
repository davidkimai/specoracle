import typing

class RetryGate:
    """
    A state machine to manage retry logic based on a maximum number of attempts.

    This class provides a simple gate-keeping mechanism to allow an action
    to be retried up to a specified maximum number of times. It tracks failures,
    resets on success, and reports whether further attempts are permitted.
    """

    def __init__(self, max_attempts: int) -> None:
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures allowed before the gate
                          closes. Must be a positive integer.

        Raises:
            TypeError: If max_attempts is not an integer.
            ValueError: If max_attempts is not positive.
        """
        if not isinstance(max_attempts, int):
            raise TypeError("max_attempts must be an integer.")
        
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive.")

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
        """Resets the failure count to zero, typically after a successful operation."""
        self._failure_count = 0

    def record_failure(self) -> None:
        """Increments the failure count by one."""
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts.

        Returns:
            The number of attempts left before allow() returns False. This will be
            zero if the failure count has reached or exceeded max_attempts.
        """
        attempts_left = self._max_attempts - self._failure_count
        return max(0, attempts_left)
