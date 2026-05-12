# -*- coding: utf-8 -*-
"""
Generates exponential backoff schedules for retrying operations.
"""

def _validate_inputs(attempts: int, base_seconds: int, cap_seconds: int) -> None:
    """
    Validates the parameters for building a retry schedule.

    Raises:
        TypeError: If any input is not an integer.
        ValueError: If inputs are outside their allowed ranges.
    """
    if not isinstance(attempts, int):
        raise TypeError("attempts must be an integer.")
    if attempts < 0:
        raise ValueError("attempts must be a non-negative integer.")

    if not isinstance(base_seconds, int):
        raise TypeError("base_seconds must be an integer.")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer.")

    if not isinstance(cap_seconds, int):
        raise TypeError("cap_seconds must be an integer.")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer.")


def _calculate_capped_delay(
    attempt_index: int, base_seconds: int, cap_seconds: int
) -> int:
    """
    Calculates a single delay for a given attempt, capped at a maximum value.

    The delay is calculated as base_seconds * (2 ** attempt_index).
    Python's arbitrary-precision integers handle the exponentiation safely.
    """
    unbounded_delay = base_seconds * (2**attempt_index)
    return min(unbounded_delay, cap_seconds)


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> list[int]:
    """
    Builds a retry schedule with exponential backoff, capped at a maximum value.

    The generated delays follow the sequence:
    base_seconds, base_seconds*2, base_seconds*4, ...

    Each delay in the sequence is capped at `cap_seconds`.

    Args:
        attempts: The number of retry attempts to generate delays for.
                  Must be a non-negative integer. If 0, an empty list is
                  returned.
        base_seconds: The initial delay in seconds. Must be a positive integer.
        cap_seconds: The maximum delay in seconds. Must be a positive integer.

    Returns:
        A list of integers representing the delay in seconds for each attempt.
        The list will have a length equal to `attempts`.

    Raises:
        TypeError: If any of the inputs are not integers.
        ValueError: If `attempts` is negative, or `base_seconds` or
                    `cap_seconds` are not positive.
    """
    _validate_inputs(attempts, base_seconds, cap_seconds)

    # The list comprehension correctly handles attempts=0 by iterating over
    # an empty range, resulting in an empty list.
    return [
        _calculate_capped_delay(i, base_seconds, cap_seconds)
        for i in range(attempts)
    ]
