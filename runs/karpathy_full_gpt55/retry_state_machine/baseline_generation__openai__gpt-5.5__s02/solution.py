class RetryGate:
    """A deterministic retry gate based on recorded failures."""

    def __init__(self, max_attempts: int):
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
            raise TypeError("max_attempts must be an integer")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        """Return True while recorded failures are less than max_attempts."""
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        """Reset the recorded failure count to zero."""
        self._failure_count = 0

    def record_failure(self) -> None:
        """Record one failure."""
        self._failure_count += 1

    def remaining(self) -> int:
        """Return the remaining attempts before allow() becomes False."""
        remaining_attempts = self._max_attempts - self._failure_count
        return remaining_attempts if remaining_attempts > 0 else 0


__all__ = ["RetryGate"]
