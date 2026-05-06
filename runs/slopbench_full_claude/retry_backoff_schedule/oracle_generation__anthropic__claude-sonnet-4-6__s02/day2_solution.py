def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return exponential backoff delays for the given number of attempts."""
    if attempts < 0:
        raise ValueError(f"attempts must be non-negative, got {attempts}")
    if base_seconds <= 0:
        raise ValueError(f"base_seconds must be positive, got {base_seconds}")
    if cap_seconds <= 0:
        raise ValueError(f"cap_seconds must be positive, got {cap_seconds}")

    delays = []
    delay = base_seconds
    for _ in range(attempts):
        delays.append(min(delay, cap_seconds))
        delay *= 2
    return delays


def next_allowed_times(start_timestamp: int, schedule: list[int]) -> list[int]:
    """Return cumulative timestamps after applying each delay in schedule."""
    times = []
    current = start_timestamp
    for delay in schedule:
        current += delay
        times.append(current)
    return times
