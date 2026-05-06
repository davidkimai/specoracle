import time


class TokenBucketEnforcer:
    """Token bucket rate limiter.

    Parameters
    ----------
    capacity:
        Maximum number of tokens the bucket can hold.
    refill_rate:
        Number of tokens added per second.
    now:
        Optional callable that returns the current time in seconds.
        Defaults to :func:`time.monotonic`.
    """

    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")

        self._capacity = capacity
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic

        self._tokens: float = float(capacity)
        self._last_refill: float = self._now()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since last refill."""
        current_time = self._now()
        elapsed = current_time - self._last_refill
        if elapsed > 0:
            new_tokens = elapsed * self._refill_rate
            self._tokens = min(self._capacity, self._tokens + new_tokens)
            self._last_refill = current_time

    def allow(self, cost: int = 1) -> bool:
        """Attempt to consume *cost* tokens from the bucket.

        Returns
        -------
        bool
            ``True`` if the request is allowed (tokens were consumed),
            ``False`` otherwise.
        """
        if cost < 0:
            raise ValueError("cost must be non-negative")

        self._refill()

        if cost <= self._tokens:
            self._tokens -= cost
            return True

        return False

    @property
    def capacity(self) -> int:
        """Maximum token capacity."""
        return self._capacity

    @property
    def refill_rate(self) -> float:
        """Token refill rate (tokens per second)."""
        return self._refill_rate

    @property
    def available_tokens(self) -> float:
        """Current number of available tokens (after refill)."""
        self._refill()
        return self._tokens
