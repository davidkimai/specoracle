"""Generates exponential backoff retry schedules."""


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> list[int]:
    """
    Builds a list of exponential backoff delays.

    The delay for attempt `i` (0-indexed) is calculated as:
    `min(base_seconds * (2**i), cap_seconds)`

    Args:
        attempts: The number of retry delays to generate. Must be a
            non-negative integer.
        base_seconds: The initial delay in seconds. Must be a positive
            integer.
        cap_seconds: The maximum delay in seconds. Must be a positive
            integer.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        Returns an empty list if attempts is 0.

    Raises:
        ValueError: If `attempts` is a negative integer, or if `base_seconds`
            or `cap_seconds` are not positive integers.
        TypeError: If any of the inputs are not integers.
    """
    if not isinstance(attempts, int):
        raise TypeError("attempts must be an integer")
    if attempts < 0:
        raise ValueError("attempts must be non-negative")

    if not isinstance(base_seconds, int):
        raise TypeError("base_seconds must be an integer")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")

    if not isinstance(cap_seconds, int):
        raise TypeError("cap_seconds must be an integer")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    schedule = []
    current_delay = base_seconds
    for _ in range(attempts):
        delay_to_use = min(current_delay, cap_seconds)
        schedule.append(delay_to_use)
        current_delay *= 2

    return schedule
