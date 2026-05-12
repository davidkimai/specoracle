class RetryGate:
    """A simple deterministic retry gate based on recorded failures."""

    def __init__(self, max_attempts: int):
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        """Return True while recorded failures are fewer than max_attempts."""
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        """Reset the recorded failure count to zero."""
        self._failures = 0

    def record_failure(self) -> None:
        """Record one failure."""
        self._failures += 1

    def remaining(self) -> int:
        """Return remaining attempts before allow() becomes False."""
        remaining_attempts = self._max_attempts - self._failures
        return remaining_attempts if remaining_attempts > 0 else 0
