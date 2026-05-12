def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    """Return exponential backoff delays capped at cap_seconds.

    Parameters
    ----------
    attempts:
        Number of retry delays to generate.  Must be non-negative.
    base_seconds:
        Starting delay in seconds.  Must be positive.
    cap_seconds:
        Maximum delay in seconds.  Must be positive.

    Returns
    -------
    list[int]
        A list of ``attempts`` delay values following exponential backoff.
    """
    if attempts < 0:
        raise ValueError(f"attempts must be non-negative, got {attempts!r}")
    if base_seconds <= 0:
        raise ValueError(f"base_seconds must be positive, got {base_seconds!r}")
    if cap_seconds <= 0:
        raise ValueError(f"cap_seconds must be positive, got {cap_seconds!r}")

    delays = []
    for i in range(attempts):
        delay = base_seconds * (2 ** i)
        delays.append(min(delay, cap_seconds))
    return delays
