class RetryGate:
    """Track retry eligibility from recorded failures."""

    __slots__ = ("_max_attempts", "_failures")

    def __init__(self, max_attempts: int):
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
        return max(0, self._max_attempts - self._failures)
