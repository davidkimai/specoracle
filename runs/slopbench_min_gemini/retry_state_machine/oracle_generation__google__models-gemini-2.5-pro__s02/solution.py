"""A state machine for managing retry attempts."""

# This module is intentionally self-contained and does not have external
# dependencies, adhering to the operational constraints of the task.


class RetryGate:
    """
    Manages state for a retry mechanism based on a maximum number of attempts.

    This class provides a simple, deterministic state machine to track failures
    and decide whether a subsequent operation should be attempted. It is useful
    for implementing retry logic in a clean, encapsulated way without relying on
    global state, time, or other external factors.
    """

    def __init__(self, max_attempts: int):
        """
        Initializes the RetryGate.

        Args:
            max_attempts: The maximum number of failures allowed before
                          the gate closes. Must be a positive integer.

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

        An attempt is allowed if the number of recorded failures is strictly
        less than the configured maximum number of attempts.

        Returns:
            True if another attempt is permitted, False otherwise.
        """
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """
        Resets the failure count to zero.

        This method should be called after a successful operation to signal
        that the retry cycle can be reset.
        """
        self._failure_count = 0

    def record_failure(self) -> None:
        """
        Increments the failure count by one.

        This method should be called after a failed operation. Each call
        consumes one of the available attempts.
        """
        self._failure_count += 1

    def remaining(self) -> int:
        """
        Calculates the number of remaining attempts.

        This represents how many more failures can be recorded before the
        `allow()` method will return False.

        Returns:
            The number of attempts left. This value can become negative if
            `record_failure()` is called more times than `max_attempts`.
        """
        return self._max_attempts - self._failure_count
