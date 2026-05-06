import time


class TokenBucketEnforcer:
    """Token bucket rate limiter.

    Parameters
    ----------
    capacity:
        Maximum number of tokens the bucket can hold.
    refill_rate:
        Number of tokens added per second.
    burst:
        Additional tokens added to the maximum capacity.
        Defaults to 0 (no burst), preserving original behavior.
    now:
        Optional callable that returns the current time in seconds.
        Defaults to :func:`time.monotonic`.
    """

    def __init__(self, capacity: int, refill_rate: float, burst: int = 0, *, now=None):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")
        if burst < 0:
            raise ValueError("burst must be non-negative")

        self._capacity = capacity
        self._burst = burst
        self._effective_capacity = capacity + burst
        self._refill_rate = refill_rate
        self._now = now if now is not None else time.monotonic

        self._tokens: float = float(self._effective_capacity)
        self._last_refill: float = self._now()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since last refill."""
        current_time = self._now()
        elapsed = current_time - self._last_refill
        if elapsed > 0:
            new_tokens = elapsed * self._refill_rate
            self._tokens = min(self._effective_capacity, self._tokens + new_tokens)
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
        """Maximum token capacity (excluding burst)."""
        return self._capacity

    @property
    def burst(self) -> int:
        """Burst capacity extension."""
        return self._burst

    @property
    def effective_capacity(self) -> int:
        """Maximum token capacity including burst."""
        return self._effective_capacity

    @property
    def refill_rate(self) -> float:
        """Token refill rate (tokens per second)."""
        return self._refill_rate

    @property
    def available_tokens(self) -> float:
        """Current number of available tokens (after refill)."""
        self._refill()
        return self._tokens
