"""
A module for timing-safe comparison of strings or bytes.
"""

import hmac
from typing import Union

__all__ = ['timing_safe_compare']


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Compares two strings or bytes objects in a way that is safe against
    timing attacks.

    This function is a typed wrapper around hmac.compare_digest. It ensures
    that both inputs are of the same type (either str or bytes) before
    performing the comparison.

    Args:
        left: The first string or bytes object to compare.
        right: The second string or bytes object to compare.

    Returns:
        True if the inputs have the same value, False otherwise.

    Raises:
        TypeError: If the inputs are not of the same type (i.e., one is str
                   and the other is bytes), or if the inputs are not str or
                   bytes at all.
    """
    if not isinstance(left, (str, bytes)) or not isinstance(right, (str, bytes)):
        raise TypeError("Inputs must be str or bytes.")

    if type(left) is not type(right):
        raise TypeError("Inputs must have the same type (both str or both bytes).")

    # hmac.compare_digest requires bytes. If inputs are strings, encode them.
    # We've already established that both inputs are of the same type.
    if isinstance(left, str):
        # We know right is also a str.
        left_bytes = left.encode('utf-8')
        right_bytes = right.encode('utf-8')
    else:
        # Inputs are already bytes.
        left_bytes = left
        right_bytes = right

    return hmac.compare_digest(left_bytes, right_bytes)
