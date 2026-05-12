"""Retry backoff schedule generation."""

from __future__ import annotations


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Build an exponential retry backoff schedule capped at a maximum delay.

    Args:
        attempts: Number of retry delays to generate. Must be non-negative.
        base_seconds: Initial delay in seconds. Must be positive.
        cap_seconds: Maximum delay in seconds. Must be positive.

    Returns:
        A list of delays in seconds, where each delay doubles from the previous
        one and is capped at cap_seconds.

    Raises:
        ValueError: If attempts is negative, or base_seconds/cap_seconds are not
        positive integers.
    """
    if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 0:
        raise ValueError("attempts must be a non-negative integer")
    if not isinstance(base_seconds, int) or isinstance(base_seconds, bool) or base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer")
    if not isinstance(cap_seconds, int) or isinstance(cap_seconds, bool) or cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer")

    schedule: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        schedule.append(min(delay, cap_seconds))
        if delay < cap_seconds:
            delay *= 2

    return schedule


__all__ = ["build_retry_schedule"]
