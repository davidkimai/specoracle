"""Utilities for building retry backoff schedules."""


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return capped exponential retry delays.

    The first delay is ``base_seconds``. Each following delay doubles until
    ``cap_seconds`` is reached.
    """
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    schedule: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        schedule.append(min(delay, cap_seconds))
        if delay < cap_seconds:
            delay *= 2

    return schedule
