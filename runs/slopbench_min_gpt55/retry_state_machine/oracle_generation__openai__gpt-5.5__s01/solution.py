class RetryGate:
    """Track retry eligibility based on a maximum number of failures."""

    def __init__(self, max_attempts: int):
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
            raise ValueError("max_attempts must be a positive integer")
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
        return max(self._max_attempts - self._failures, 0)
