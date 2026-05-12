def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return exponential backoff delays capped at cap_seconds."""
    if attempts < 0:
        raise ValueError(f"attempts must be non-negative, got {attempts}")
    if base_seconds <= 0:
        raise ValueError(f"base_seconds must be positive, got {base_seconds}")
    if cap_seconds <= 0:
        raise ValueError(f"cap_seconds must be positive, got {cap_seconds}")

    return [min(base_seconds * (2 ** i), cap_seconds) for i in range(attempts)]
