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
        self._tokens = float(capacity)
        self._now = now if now is not None else time.monotonic
        self._last_refill = self._now()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since last call."""
        current_time = self._now()
        elapsed = current_time - self._last_refill
        if elapsed > 0:
            added = elapsed * self._refill_rate
            self._tokens = min(self._capacity, self._tokens + added)
            self._last_refill = current_time

    def allow(self, cost: int = 1) -> bool:
        """Attempt to consume *cost* tokens from the bucket.

        Parameters
        ----------
        cost:
            Number of tokens to consume. Must be a positive integer.

        Returns
        -------
        bool
            ``True`` if the tokens were consumed successfully,
            ``False`` if the bucket did not have enough tokens.
        """
        if cost <= 0:
            raise ValueError("cost must be a positive integer")

        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    @property
    def capacity(self) -> int:
        """Maximum token capacity of the bucket."""
        return self._capacity

    @property
    def refill_rate(self) -> float:
        """Token refill rate in tokens per second."""
        return self._refill_rate

    @property
    def available_tokens(self) -> float:
        """Current number of available tokens (after refill)."""
        self._refill()
        return self._tokens
