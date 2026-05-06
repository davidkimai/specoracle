def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return exponential backoff delays capped at cap_seconds.

    Parameters
    ----------
    attempts:     number of retry delays to generate (non-negative)
    base_seconds: starting delay in seconds (positive)
    cap_seconds:  maximum delay in seconds (positive)

    Returns
    -------
    List of integer delays of length *attempts*.
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
