"""
A module for building exponential backoff retry schedules.
"""

from __future__ import annotations

__all__ = ["build_retry_schedule"]


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> list[int]:
    """
    Generates a list of delays for an exponential backoff retry strategy.

    The delay for the i-th attempt (0-indexed) is calculated as:
    min(base_seconds * (2 ** i), cap_seconds)

    Args:
        attempts: The total number of retry attempts. Must be non-negative.
        base_seconds: The base delay in seconds for the first attempt.
                      Must be positive.
        cap_seconds: The maximum possible delay in seconds. Must be positive.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        Returns an empty list if attempts is 0.

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

    return [min(base_seconds * (2**i), cap_seconds) for i in range(attempts)]
