# timing_safe_compare.py

"""
A secure, typed wrapper for constant-time string and bytes comparison.
"""

import hmac
from typing import Union


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Performs a constant-time comparison of two strings or byte sequences.

    This function is a typed wrapper around hmac.compare_digest to prevent
    timing attacks. It requires both inputs to be of the same type, either
    str or bytes.

    Args:
        left: The first string or bytes object to compare.
        right: The second string or bytes object to compare.

    Returns:
        True if the inputs are equal, False otherwise.

    Raises:
        TypeError: If the inputs are not of the same type (both str or
                   both bytes), or if they are of an unsupported type.
    """
    if type(left) is not type(right):
        raise TypeError(
            "Inputs must be of the same type. "
            f"Got {type(left).__name__} and {type(right).__name__}."
        )

    if isinstance(left, str):
        # hmac.compare_digest requires bytes. If inputs are strings,
        # we must encode them. UTF-8 is a safe default.
        left_bytes = left.encode('utf-8')
        right_bytes = right.encode('utf-8')
    elif isinstance(left, bytes):
        left_bytes = left
        right_bytes = right
    else:
        raise TypeError(
            f"Inputs must be str or bytes, not {type(left).__name__}."
        )

    return hmac.compare_digest(left_bytes, right_bytes)
