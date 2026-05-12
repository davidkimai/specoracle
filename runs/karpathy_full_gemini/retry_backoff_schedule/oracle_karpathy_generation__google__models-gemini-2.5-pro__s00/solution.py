"""
A module for generating exponential backoff retry schedules.
"""

from typing import List


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> List[int]:
    """
    Generates a list of integer delays for an exponential backoff strategy.

    The delay for the i-th attempt (0-indexed) is calculated as:
    min(base_seconds * (2 ** i), cap_seconds)

    Args:
        attempts: The total number of retry attempts. Must be a non-negative
                  integer.
        base_seconds: The base delay in seconds for the first attempt. Must be
                      a positive integer.
        cap_seconds: The maximum delay in seconds for any attempt. Must be a
                     positive integer.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        The list will have a length equal to `attempts`.

    Raises:
        ValueError: If `attempts` is negative, or if `base_seconds` or
                    `cap_seconds` are not positive.
    """
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")

    return [
        min(base_seconds * (2**i), cap_seconds) for i in range(attempts)
    ]
