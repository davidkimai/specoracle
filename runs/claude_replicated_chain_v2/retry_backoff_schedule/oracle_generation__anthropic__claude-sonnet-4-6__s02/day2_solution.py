def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return exponential backoff delays capped at cap_seconds.

    Parameters
    ----------
    attempts:     number of retry delays to generate (non-negative)
    base_seconds: starting delay in seconds (positive)
    cap_seconds:  maximum delay in seconds (positive)

    Returns
    -------
    List of delay values: base, base*2, base*4, ... each capped at cap_seconds.
    """
    if attempts < 0:
        raise ValueError(f"attempts must be non-negative, got {attempts}")
    if base_seconds <= 0:
        raise ValueError(f"base_seconds must be positive, got {base_seconds}")
    if cap_seconds <= 0:
        raise ValueError(f"cap_seconds must be positive, got {cap_seconds}")

    schedule = []
    for i in range(attempts):
        delay = base_seconds * (2 ** i)
        schedule.append(min(delay, cap_seconds))
    return schedule


def next_allowed_times(start_timestamp: int, schedule: list[int]) -> list[int]:
    """Return cumulative timestamps after applying each delay in schedule.

    Parameters
    ----------
    start_timestamp: the initial Unix timestamp (integer seconds)
    schedule:        list of delay values in seconds

    Returns
    -------
    List of timestamps where each entry is the cumulative sum of
    start_timestamp plus all delays up to and including that position.
    """
    times = []
    current = start_timestamp
    for delay in schedule:
        current += delay
        times.append(current)
    return times
