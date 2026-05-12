from __future__ import annotations

__all__ = ["build_retry_schedule"]


def _ensure_int(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """
    Build an exponential retry backoff schedule.

    Delays start at ``base_seconds`` and double each attempt, with each delay
    capped at ``cap_seconds``. If ``attempts`` is 0, an empty list is returned.

    Raises:
        ValueError: If attempts is negative, or if base_seconds/cap_seconds are
            not positive integers.
    """
    _ensure_int("attempts", attempts)
    _ensure_int("base_seconds", base_seconds)
    _ensure_int("cap_seconds", cap_seconds)

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
