def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Build an exponential retry backoff schedule capped at cap_seconds.

    Args:
        attempts: Number of retry delays to produce. Must be non-negative.
        base_seconds: Initial delay in seconds. Must be positive.
        cap_seconds: Maximum delay in seconds. Must be positive.

    Returns:
        A list of retry delays in seconds.

    Raises:
        ValueError: If attempts is negative or if base_seconds/cap_seconds are not
            positive integers.
    """
    if (
        not isinstance(attempts, int)
        or isinstance(attempts, bool)
        or attempts < 0
    ):
        raise ValueError("attempts must be a non-negative integer")

    if (
        not isinstance(base_seconds, int)
        or isinstance(base_seconds, bool)
        or base_seconds <= 0
    ):
        raise ValueError("base_seconds must be a positive integer")

    if (
        not isinstance(cap_seconds, int)
        or isinstance(cap_seconds, bool)
        or cap_seconds <= 0
    ):
        raise ValueError("cap_seconds must be a positive integer")

    schedule: list[int] = []
    delay = base_seconds

    for _ in range(attempts):
        current = delay if delay < cap_seconds else cap_seconds
        schedule.append(current)

        if delay < cap_seconds:
            delay *= 2

    return schedule
