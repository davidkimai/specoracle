def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return exponential backoff delays capped at cap_seconds.

    Args:
        attempts: Number of retry delays to generate (non-negative).
        base_seconds: Starting delay in seconds (positive).
        cap_seconds: Maximum delay in seconds (positive).

    Returns:
        List of integer delay values of length `attempts`.

    Raises:
        ValueError: If any argument fails validation.
    """
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
    """Return cumulative timestamps after applying each delay in schedule.

    Args:
        start_timestamp: The initial Unix timestamp (integer).
        schedule: List of integer delays (e.g. from build_retry_schedule).

    Returns:
        List of integer timestamps, one per entry in schedule, where each
        timestamp is the sum of start_timestamp and all delays up to and
        including that entry.
    """
    timestamps = []
    current = start_timestamp
    for delay in schedule:
        current += delay
        timestamps.append(current)
    return timestamps
