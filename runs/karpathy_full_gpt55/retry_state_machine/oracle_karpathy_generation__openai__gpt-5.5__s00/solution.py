class RetryGate:
    def __init__(self, max_attempts: int):
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
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
