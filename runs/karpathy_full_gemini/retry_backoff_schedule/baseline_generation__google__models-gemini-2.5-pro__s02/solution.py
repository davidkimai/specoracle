"""
A module for calculating exponential backoff retry schedules.
"""

# This module uses type hints and is intended for Python 3.9+
# where list can be used as a generic type.


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> list[int]:
    """Generates a list of delays for an exponential backoff schedule.

    This function calculates a series of delays, where each subsequent delay
    is double the previous one, up to a specified maximum cap. This is
    commonly used in retry logic for network requests or other fallible
    operations.

    Args:
        attempts: The number of retry attempts to generate a schedule for.
                  Must be a non-negative integer. An input of 0 will result
                  in an empty list.
        base_seconds: The base delay in seconds for the first attempt.
                      This value is doubled for each subsequent attempt.
                      Must be a positive integer.
        cap_seconds: The maximum (or "cap") delay in seconds. The calculated
                     delay for any attempt will not exceed this value.
                     Must be a positive integer.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        The length of the list will be equal to the `attempts` argument.
        For example, `build_retry_schedule(4, 1, 10)` would return
        `[1, 2, 4, 8]`.

    Raises:
        ValueError: If `attempts` is negative, or if `base_seconds` or
                    `cap_seconds` are not positive integers.
    """
    if not isinstance(attempts, int) or attempts < 0:
        raise ValueError("attempts must be a non-negative integer")
    if not isinstance(base_seconds, int) or base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer")
    if not isinstance(cap_seconds, int) or cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer")

    # A list comprehension provides a concise way to generate the schedule.
    # The range(attempts) correctly handles the case where attempts is 0,
    # resulting in an empty list.
    return [min(base_seconds * (2**i), cap_seconds) for i in range(attempts)]
