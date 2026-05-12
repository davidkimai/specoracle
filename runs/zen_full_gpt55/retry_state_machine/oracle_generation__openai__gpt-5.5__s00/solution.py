class RetryGate:
    """Track retry attempts using a simple failure counter."""

    def __init__(self, max_attempts: int):
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
            raise ValueError("max_attempts must be a positive integer")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        self._max_attempts = max_attempts
        self._failure_count = 0

    def allow(self) -> bool:
        return self._failure_count < self._max_attempts

    def record_success(self) -> None:
        self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1

    def remaining(self) -> int:
        return max(0, self._max_attempts - self._failure_count)


__all__ = ["RetryGate"]
