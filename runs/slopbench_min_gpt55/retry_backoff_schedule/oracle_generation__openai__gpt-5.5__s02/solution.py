__all__ = ["build_retry_schedule"]


def _require_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")


def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    _require_integer("attempts", attempts)
    _require_integer("base_seconds", base_seconds)
    _require_integer("cap_seconds", cap_seconds)

    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    delays: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        delays.append(min(delay, cap_seconds))
        if delay < cap_seconds:
            delay *= 2

    return delays
