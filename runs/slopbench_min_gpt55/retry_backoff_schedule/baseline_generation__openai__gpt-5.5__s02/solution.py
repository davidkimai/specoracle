"""Retry backoff schedule builder."""

from __future__ import annotations


def _validate_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Build an exponential retry backoff schedule capped at cap_seconds.

    Args:
        attempts: Number of retry delays to produce. Must be non-negative.
        base_seconds: Initial delay in seconds. Must be positive.
        cap_seconds: Maximum delay in seconds. Must be positive.

    Returns:
        A list of retry delays in seconds.
    """
    _validate_int("attempts", attempts)
    _validate_int("base_seconds", base_seconds)
    _validate_int("cap_seconds", cap_seconds)

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
        delay = min(delay * 2, cap_seconds) if delay < cap_seconds else cap_seconds

    return schedule


__all__ = ["build_retry_schedule"]
