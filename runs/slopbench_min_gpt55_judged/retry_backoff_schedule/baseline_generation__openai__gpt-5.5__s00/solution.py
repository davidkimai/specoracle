"""Retry backoff schedule generation."""

from __future__ import annotations


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Build an exponential retry backoff schedule capped at ``cap_seconds``.

    Args:
        attempts: Number of retry delays to produce. Must be non-negative.
        base_seconds: Initial delay in seconds. Must be positive.
        cap_seconds: Maximum delay in seconds. Must be positive.

    Returns:
        A list of retry delays. For example, with attempts=4, base_seconds=2,
        and cap_seconds=10, the result is [2, 4, 8, 10].

    Raises:
        ValueError: If attempts is negative, or base_seconds/cap_seconds are not
        positive integers.
    """
    if not isinstance(attempts, int) or isinstance(attempts, bool):
        raise ValueError("attempts must be a non-negative integer")
    if not isinstance(base_seconds, int) or isinstance(base_seconds, bool):
        raise ValueError("base_seconds must be a positive integer")
    if not isinstance(cap_seconds, int) or isinstance(cap_seconds, bool):
        raise ValueError("cap_seconds must be a positive integer")

    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    schedule: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        schedule.append(delay if delay <= cap_seconds else cap_seconds)
        if delay < cap_seconds:
            delay *= 2

    return schedule


__all__ = ["build_retry_schedule"]
