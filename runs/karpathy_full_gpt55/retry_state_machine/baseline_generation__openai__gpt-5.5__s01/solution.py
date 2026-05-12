class RetryGate:
    """A simple deterministic retry gate based on recorded failures."""

    __slots__ = ("_max_attempts", "_failures")

    def __init__(self, max_attempts: int):
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        """Return True while recorded failures are less than max_attempts."""
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        """Reset the recorded failure count to zero."""
        self._failures = 0

    def record_failure(self) -> None:
        """Increment the recorded failure count by one."""
        self._failures += 1

    def remaining(self) -> int:
        """Return remaining failures that can be recorded before allow() is False."""
        remaining_attempts = self._max_attempts - self._failures
        return remaining_attempts if remaining_attempts > 0 else 0
