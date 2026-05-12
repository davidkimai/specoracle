"""
A module for timing-safe string comparison.
"""

import hmac
from typing import Union


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Performs a timing-safe comparison of two strings or byte strings.

    This function is a typed wrapper around hmac.compare_digest. It ensures
    that both inputs are of the same type (either both str or both bytes)
    before performing the comparison. This helps prevent subtle bugs that can
    arise from comparing different data types.

    Args:
        left: The first string or byte string to compare.
        right: The second string or byte string to compare.

    Returns:
        True if the inputs have the same value, False otherwise.

    Raises:
        TypeError: If the inputs are not of the same type (both str or
                   both bytes), or if they are of an unsupported type.
    """
    if isinstance(left, str):
        if not isinstance(right, str):
            raise TypeError("Inputs must have the same type, both str or both bytes.")
        # Both are strings, encode to bytes for comparison.
        # Using a standard, fixed encoding like UTF-8 is important for consistency.
        left_bytes = left.encode('utf-8')
        right_bytes = right.encode('utf-8')
    elif isinstance(left, bytes):
        if not isinstance(right, bytes):
            raise TypeError("Inputs must have the same type, both str or both bytes.")
        # Both are bytes, use them directly.
        left_bytes = left
        right_bytes = right
    else:
        raise TypeError("Inputs must be of type str or bytes.")

    return hmac.compare_digest(left_bytes, right_bytes)
