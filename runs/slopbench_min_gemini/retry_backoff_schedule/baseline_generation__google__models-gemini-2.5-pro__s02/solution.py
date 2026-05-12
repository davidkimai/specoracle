"""
A module for generating exponential backoff retry schedules.
"""

__all__ = ["build_retry_schedule"]


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> list[int]:
    """
    Generates a list of delays for an exponential backoff retry strategy.

    Validates that attempts is non-negative and base_seconds/cap_seconds are
    positive, otherwise raises ValueError. Returns exponential backoff delays:
    base_seconds, base_seconds*2, base_seconds*4, ... capped at cap_seconds.
    attempts=0 returns an empty list.

    Args:
        attempts: The number of retry attempts. Must be a non-negative integer.
        base_seconds: The initial delay in seconds. Must be a positive integer.
        cap_seconds: The maximum delay in seconds. Must be a positive integer.

    Returns:
        A list of integers representing the delay in seconds for each attempt.

    Raises:
        ValueError: If attempts is negative, or if base_seconds or
                    cap_seconds are not positive.
    """
    if not isinstance(attempts, int) or attempts < 0:
        raise ValueError("attempts must be a non-negative integer")
    if not isinstance(base_seconds, int) or base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer")
    if not isinstance(cap_seconds, int) or cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer")

    # The formula for the delay at attempt i (0-indexed) is:
    # min(cap_seconds, base_seconds * (2**i))
    # A list comprehension provides a concise and readable implementation.
    # range(0) correctly produces an empty list for attempts=0.
    return [min(cap_seconds, base_seconds * (2**i)) for i in range(attempts)]
