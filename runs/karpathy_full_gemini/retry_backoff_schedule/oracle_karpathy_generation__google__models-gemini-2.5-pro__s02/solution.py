"""
A module for generating exponential backoff retry schedules.
"""

import typing


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> typing.List[int]:
    """
    Generates a list of delays for an exponential backoff retry strategy.

    The delays follow the sequence: base, base*2, base*4, ..., with each
    delay capped at cap_seconds.

    Args:
        attempts: The number of retry attempts to generate delays for. Must be
                  non-negative.
        base_seconds: The initial delay in seconds. Must be positive.
        cap_seconds: The maximum delay in seconds. Must be positive.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        The list will be empty if attempts is 0.

    Raises:
        ValueError: If attempts is negative, or if base_seconds or
                    cap_seconds are not positive.
    """
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    return [min(base_seconds * (2**i), cap_seconds) for i in range(attempts)]
