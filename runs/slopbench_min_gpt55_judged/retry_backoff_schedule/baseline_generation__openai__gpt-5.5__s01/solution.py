"""Retry backoff schedule builder."""

from __future__ import annotations


def _require_int(name: str, value: int) -> None:
    """Validate that a value is an integer, excluding bool."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """
    Build an exponential retry backoff schedule.

    Delays start at ``base_seconds`` and double for each subsequent attempt,
    with every delay capped at ``cap_seconds``.

    Args:
        attempts: Number of retry delays to return. Must be non-negative.
        base_seconds: Initial delay in seconds. Must be positive.
        cap_seconds: Maximum delay in seconds. Must be positive.

    Returns:
        A list of retry delays in seconds.

    Raises:
        ValueError: If any argument is not an integer, or if ``attempts`` is
            negative, or if ``base_seconds`` / ``cap_seconds`` are not positive.
    """
    _require_int("attempts", attempts)
    _require_int("base_seconds", base_seconds)
    _require_int("cap_seconds", cap_seconds)

    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    schedule: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        schedule.append(delay if delay < cap_seconds else cap_seconds)
        if delay < cap_seconds:
            delay *= 2

    return schedule
