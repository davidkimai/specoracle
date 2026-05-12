class RetryGate:
    """A simple retry state machine that tracks failures against a maximum."""

    def __init__(self, max_attempts: int) -> None:
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be positive, got {max_attempts}")
        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        """Return True while failures recorded are less than max_attempts."""
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        """Reset the failure count to zero."""
        self._failures = 0

    def record_failure(self) -> None:
        """Increment the failure count by one."""
        self._failures += 1

    def remaining(self) -> int:
        """Return the number of remaining attempts before allow() becomes False."""
        return max(0, self._max_attempts - self._failures)
