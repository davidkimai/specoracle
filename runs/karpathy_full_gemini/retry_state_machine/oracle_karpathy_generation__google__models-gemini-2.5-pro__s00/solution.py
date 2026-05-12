# retry_state_machine.py

"""
A simple state machine for managing retries.
"""

class RetryGate:
    """
    Manages retry logic based on a maximum number of attempts.

    This class provides a stateful gate to control whether an action should be
    retried based on a simple count of consecutive failures. The state is
    entirely self-contained and deterministic.
    """

    def __init__(self, max_attempts: int):
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures allowed before the gate
                          closes (i.e., `allow()` returns False). Must be a
                          positive integer.

        Raises:
            ValueError: If `max_attempts` is not a positive integer.
        """
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer.")
        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        """
        Checks if another attempt is allowed.

        Returns:
            True if the number of recorded failures is less than `max_attempts`,
            False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """
        Resets the failure count to zero.

        This method should be called after a successful attempt to reset the
        retry counter.
        """
        self._failure_count = 0

    def record_failure(self) -> None:
        """
        Increments the failure count by one.

        This method should be called after a failed attempt.
        """
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts before the gate closes.

        Returns:
            The number of attempts left before `allow()` returns False.
            This will be 0 if the gate is already closed.
        """
        remaining_count = self._max_attempts - self._failure_count
        return max(0, remaining_count)
