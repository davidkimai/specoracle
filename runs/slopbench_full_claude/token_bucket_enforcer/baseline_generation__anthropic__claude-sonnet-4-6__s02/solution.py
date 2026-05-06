import time


class TokenBucketEnforcer:
    """Token bucket rate limiter.

    Parameters
    ----------
    capacity : int
        Maximum number of tokens the bucket can hold.
    refill_rate : float
        Tokens added per second.
    now : callable, optional
        Zero-argument callable returning the current time in seconds.
        Defaults to :func:`time.monotonic`.
    """

    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")

        self._capacity = capacity
        self._refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._now = now if now is not None else time.monotonic
        self._last_refill = self._now()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since the last call."""
        current = self._now()
        elapsed = current - self._last_refill
        if elapsed > 0:
            self._tokens = min(
                float(self._capacity),
                self._tokens + elapsed * self._refill_rate,
            )
            self._last_refill = current

    def allow(self, cost: int = 1) -> bool:
        """Check whether *cost* tokens are available and consume them if so.

        Parameters
        ----------
        cost : int
            Number of tokens required for this request.

        Returns
        -------
        bool
            ``True`` if the request is allowed, ``False`` otherwise.
        """
        if cost < 0:
            raise ValueError("cost must be non-negative")

        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    @property
    def tokens(self) -> float:
        """Current token count (read-only, after refill)."""
        self._refill()
        return self._tokens

    @property
    def capacity(self) -> int:
        """Maximum bucket capacity."""
        return self._capacity

    @property
    def refill_rate(self) -> float:
        """Token refill rate in tokens per second."""
        return self._refill_rate
