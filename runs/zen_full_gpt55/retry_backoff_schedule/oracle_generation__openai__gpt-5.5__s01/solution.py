"""Utilities for building retry backoff schedules."""


def _require_integer(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _require_non_negative(name: str, value: int) -> int:
    value = _require_integer(name, value)
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _require_positive(name: str, value: int) -> int:
    value = _require_integer(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def build_retry_schedule(
    attempts: int,
    base_seconds: int,
    cap_seconds: int,
) -> list[int]:
    """Return capped exponential retry delays for the requested attempts."""
    attempts = _require_non_negative("attempts", attempts)
    base_seconds = _require_positive("base_seconds", base_seconds)
    cap_seconds = _require_positive("cap_seconds", cap_seconds)

    schedule: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        schedule.append(min(delay, cap_seconds))

        if delay >= cap_seconds or delay > cap_seconds // 2:
            delay = cap_seconds
        else:
            delay *= 2

    return schedule
