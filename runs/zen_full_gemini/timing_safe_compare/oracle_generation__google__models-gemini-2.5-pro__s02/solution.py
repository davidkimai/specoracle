"""
A module for timing-safe string and bytes comparison.
"""

import hmac
from typing import Union


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Compares two values in a way that is resistant to timing attacks.

    This function is a typed wrapper around hmac.compare_digest. It requires
    both inputs to be of the same type, either str or bytes.

    Args:
        left: The first value to compare.
        right: The second value to compare.

    Returns:
        True if the inputs are of the same supported type and are equal,
        False otherwise.

    Raises:
        TypeError: If the inputs are not both of type str or both of type bytes.
    """
    left_bytes: bytes
    right_bytes: bytes

    if isinstance(left, str) and isinstance(right, str):
        left_bytes = left.encode('utf-8')
        right_bytes = right.encode('utf-8')
    elif isinstance(left, bytes) and isinstance(right, bytes):
        left_bytes = left
        right_bytes = right
    else:
        raise TypeError(
            "Both inputs must be of type str, or both must be of type bytes."
        )

    return hmac.compare_digest(left_bytes, right_bytes)
