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
        Optional callable that returns the current time as a float (seconds).
        Defaults to :func:`time.monotonic`.  Useful for testing.
    """

    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be a positive number")

        self._capacity = capacity
        self._refill_rate = refill_rate
        self._tokens = float(capacity)
        self._now = now if now is not None else time.monotonic
        self._last_refill = self._now()

    def _refill(self) -> None:
        """Add tokens proportional to elapsed time since the last call."""
        current = self._now()
        elapsed = current - self._last_refill
        if elapsed > 0:
            self._tokens = min(
                float(self._capacity),
                self._tokens + elapsed * self._refill_rate,
            )
            self._last_refill = current

    def allow(self, cost: int = 1) -> bool:
        """Attempt to consume *cost* tokens from the bucket.

        Returns
        -------
        bool
            ``True`` if the tokens were consumed; ``False`` if there are not
            enough tokens available.
        """
        if cost < 0:
            raise ValueError("cost must be a non-negative integer")

        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

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
        """Current token count (after a refill step)."""
        self._refill()
        return self._tokens
