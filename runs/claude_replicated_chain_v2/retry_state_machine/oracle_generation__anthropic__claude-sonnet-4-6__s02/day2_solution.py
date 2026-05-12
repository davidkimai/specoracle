"""retry_state_machine: a simple retry gate based on failure counting."""


class RetryGate:
    """Tracks failures and decides whether further attempts are allowed."""

    def __init__(self, max_attempts: int) -> None:
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be positive, got {max_attempts}")
        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        """Return True while recorded failures are below max_attempts."""
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        """Reset the failure count to zero."""
        self._failures = 0

    def record_failure(self) -> None:
        """Increment the failure count by one."""
        self._failures += 1

    def remaining(self) -> int:
        """Return the number of failures still allowed before allow() is False."""
        return max(0, self._max_attempts - self._failures)

    def snapshot(self) -> dict:
        """Return the current state as a dictionary without mutating it."""
        return {
            "max_attempts": self._max_attempts,
            "failures": self._failures,
            "remaining": self.remaining(),
            "allowed": self.allow(),
        }
