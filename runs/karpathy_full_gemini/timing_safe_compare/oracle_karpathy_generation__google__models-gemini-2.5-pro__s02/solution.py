"""
A module for performing timing-safe string and bytes comparison.
"""

import hmac
from typing import Union

def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Performs a timing-safe comparison of two strings or byte strings.

    This function is a typed wrapper around hmac.compare_digest. It requires
    that both inputs are of the same type, either str or bytes.

    Args:
        left: The first string or bytes object to compare.
        right: The second string or bytes object to compare.

    Returns:
        True if the inputs are equal, False otherwise.

    Raises:
        TypeError: If the inputs are not of the same type (both must be
                   str or both must be bytes), or if the inputs are not
                   of type str or bytes.
    """
    if type(left) is not type(right):
        raise TypeError("Inputs must have the same type.")

    if isinstance(left, str):
        # We know `right` is also a str due to the type check above.
        left_bytes = left.encode('utf-8')
        right_bytes = right.encode('utf-8')
    elif isinstance(left, bytes):
        left_bytes = left
        right_bytes = right
    else:
        raise TypeError("Inputs must be str or bytes.")

    return hmac.compare_digest(left_bytes, right_bytes)
