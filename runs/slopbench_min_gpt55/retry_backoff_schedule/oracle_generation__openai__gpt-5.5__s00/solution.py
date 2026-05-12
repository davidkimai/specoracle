"""Build exponential retry backoff schedules."""

__all__ = ["build_retry_schedule"]


def _require_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")


def _validate_inputs(attempts: int, base_seconds: int, cap_seconds: int) -> None:
    _require_int("attempts", attempts)
    _require_int("base_seconds", base_seconds)
    _require_int("cap_seconds", cap_seconds)

    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")


def build_retry_schedule(
    attempts: int,
    base_seconds: int,
    cap_seconds: int,
) -> list[int]:
    """Return capped exponential backoff delays for the requested attempts."""
    _validate_inputs(attempts, base_seconds, cap_seconds)

    delays: list[int] = []
    delay = min(base_seconds, cap_seconds)

    for _ in range(attempts):
        delays.append(delay)
        if delay < cap_seconds:
            delay = min(delay * 2, cap_seconds)

    return delays
