class RetryGate:
    """A deterministic retry gate based on consecutive recorded failures."""

    def __init__(self, max_attempts: int):
        if not isinstance(max_attempts, int):
            raise TypeError("max_attempts must be an integer")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        """Return True if another attempt is currently allowed."""
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        """Reset the recorded failure count to zero."""
        self._failures = 0

    def record_failure(self) -> None:
        """Record one failure."""
        self._failures += 1

    def remaining(self) -> int:
        """Return the number of failures remaining before attempts are disallowed."""
        remaining = self._max_attempts - self._failures
        return remaining if remaining > 0 else 0
