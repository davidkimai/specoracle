class RetryGate:
    """Track retry eligibility based on consecutive recorded failures."""

    __slots__ = ("_max_attempts", "_failures")

    def __init__(self, max_attempts: int) -> None:
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
            raise TypeError("max_attempts must be an integer")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        self._max_attempts = max_attempts
        self._failures = 0

    def allow(self) -> bool:
        return self._failures < self._max_attempts

    def record_success(self) -> None:
        self._failures = 0

    def record_failure(self) -> None:
        self._failures += 1

    def remaining(self) -> int:
        remaining_attempts = self._max_attempts - self._failures
        return max(0, remaining_attempts)

    def snapshot(self) -> dict:
        return {
            "max_attempts": self._max_attempts,
            "failures": self._failures,
            "remaining": self.remaining(),
            "allowed": self.allow(),
        }


__all__ = ["RetryGate"]
