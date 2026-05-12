# retry_backoff_schedule.py

"""Generates exponential backoff schedules for retries."""

from typing import List

__all__ = ["build_retry_schedule"]


def _validate_parameters(
    attempts: int, base_seconds: int, cap_seconds: int
) -> None:
    """
    Validates the parameters for building a retry schedule.

    Raises:
        ValueError: If any parameter is invalid.
    """
    if not isinstance(attempts, int) or attempts < 0:
        raise ValueError("attempts must be a non-negative integer")
    if not isinstance(base_seconds, int) or base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer")
    if not isinstance(cap_seconds, int) or cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer")


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> List[int]:
    """
    Builds a list of delays for an exponential backoff retry strategy.

    The delay for attempt `i` (0-indexed) is calculated as:
    `min(base_seconds * (2 ** i), cap_seconds)`

    Args:
        attempts: The number of retry delays to generate. Must be non-negative.
        base_seconds: The base delay in seconds for the first attempt.
                      Must be positive.
        cap_seconds: The maximum delay in seconds. Must be positive.

    Returns:
        A list of integers, where each integer is the calculated delay
        in seconds for the corresponding retry attempt. An empty list is
        returned if `attempts` is 0.

    Raises:
        ValueError: If `attempts` is negative, or if `base_seconds` or
                    `cap_seconds` are not positive integers.
    """
    _validate_parameters(attempts, base_seconds, cap_seconds)

    return [
        min(base_seconds * (2**i), cap_seconds)
        for i in range(attempts)
    ]
