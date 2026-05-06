"""
token_bucket_enforcer.py

Implements a token bucket rate limiter.
"""

import time


class TokenBucketEnforcer:
    """
    Token bucket rate limiter.

    Parameters
    ----------
    capacity : int
        Maximum number of tokens the bucket can hold.
    refill_rate : float
        Number of tokens added per second.
    now : callable, optional
        Zero-argument callable returning the current time in seconds.
        Defaults to ``time.monotonic``.  Useful for testing.
    """

    def __init__(self, capacity: int, refill_rate: float, *, now=None):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")

        self._capacity = capacity
        self._refill_rate = float(refill_rate)
        self._now = now if now is not None else time.monotonic

        # Start with a full bucket.
        self._tokens: float = float(capacity)
        self._last_refill: float = self._now()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _refill(self) -> None:
        """Add tokens based on elapsed time, capped at capacity."""
        current = self._now()
        elapsed = current - self._last_refill
        if elapsed > 0:
            self._tokens = min(
                float(self._capacity),
                self._tokens + elapsed * self._refill_rate,
            )
            self._last_refill = current

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow(self, cost: int = 1) -> bool:
        """
        Attempt to consume *cost* tokens from the bucket.

        Parameters
        ----------
        cost : int
            Number of tokens to consume.  Must be a positive integer.

        Returns
        -------
        bool
            ``True`` if enough tokens were available and have been
            consumed; ``False`` otherwise (bucket is unchanged on
            denial).
        """
        if cost <= 0:
            raise ValueError("cost must be a positive integer")

        self._refill()

        if cost > self._tokens:
            return False

        self._tokens -= cost
        return True

    # ------------------------------------------------------------------
    # Properties (read-only inspection)
    # ------------------------------------------------------------------

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
        """
        Current token count after a refill.

        Note: calling this property triggers a refill calculation.
        """
        self._refill()
        return self._tokens
