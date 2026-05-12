"""Module to generate exponential backoff retry schedules."""

from __future__ import annotations

import math
from typing import List


def _validate_inputs(attempts: int, base_seconds: int, cap_seconds: int) -> None:
    """
    Raise ValueError if inputs for the schedule are invalid.

    Args:
        attempts: The number of retry attempts. Must be non-negative.
        base_seconds: The base delay in seconds. Must be positive.
        cap_seconds: The maximum delay in seconds. Must be positive.

    Raises:
        ValueError: If any argument fails validation.
    """
    if not isinstance(attempts, int) or attempts < 0:
        raise ValueError("attempts must be a non-negative integer")
    if not isinstance(base_seconds, int) or base_seconds <= 0:
        raise ValueError("base_seconds must be a positive integer")
    if not isinstance(cap_seconds, int) or cap_seconds <= 0:
        raise ValueError("cap_seconds must be a positive integer")


def _calculate_capped_delay(
    attempt_index: int, base_seconds: int, cap_seconds: int
) -> int:
    """
    Calculate the exponential backoff delay for a single attempt, with a cap.

    The delay is calculated as `base_seconds * (2 ** attempt_index)`.

    Args:
        attempt_index: The zero-based index of the current attempt.
        base_seconds: The base delay in seconds.
        cap_seconds: The maximum delay in seconds.

    Returns:
        The calculated delay, capped at cap_seconds.
    """
    # Using math.pow returns a float, so we ensure int arithmetic.
    unbounded_delay = base_seconds * (2**attempt_index)
    return min(unbounded_delay, cap_seconds)


def build_retry_schedule(
    attempts: int, base_seconds: int, cap_seconds: int
) -> List[int]:
    """
    Generate a list of retry delays using an exponential backoff strategy.

    The generated delays follow the pattern:
    [base, base*2, base*4, ..., cap]
    where each delay is capped at `cap_seconds`.

    Args:
        attempts: The total number of retry attempts to schedule.
            If 0, an empty list is returned.
        base_seconds: The initial delay in seconds for the first attempt.
        cap_seconds: The maximum delay in seconds for any single attempt.

    Returns:
        A list of integers representing the delay in seconds for each attempt.

    Raises:
        ValueError: If `attempts` is negative, or if `base_seconds` or
            `cap_seconds` are not positive integers.
    """
    _validate_inputs(attempts, base_seconds, cap_seconds)

    if attempts == 0:
        return []

    return [
        _calculate_capped_delay(i, base_seconds, cap_seconds)
        for i in range(attempts)
    ]
