"""
A module for timing-safe string comparison.
"""

import hmac
from typing import Union


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Compares two strings or byte strings in a way that is safe against
    timing attacks.

    This is a typed wrapper around hmac.compare_digest.

    Args:
        left: The first string or byte string to compare.
        right: The second string or byte string to compare.

    Returns:
        True if the two values are equal, False otherwise.

    Raises:
        TypeError: If the inputs are not both of type str or both of type bytes.
    """
    if type(left) is not type(right):
        raise TypeError("Both inputs must have the same type (str or bytes).")

    if isinstance(left, str):
        # We know right is also a str due to the check above.
        # hmac.compare_digest requires bytes, so we encode strings.
        # UTF-8 is a safe, standard choice.
        left_bytes = left.encode('utf-8')
        right_bytes = right.encode('utf-8')
        return hmac.compare_digest(left_bytes, right_bytes)
    elif isinstance(left, bytes):
        # Inputs are already bytes, pass them directly.
        return hmac.compare_digest(left, right)
    else:
        # This case handles types that are neither str nor bytes.
        raise TypeError("Inputs must be of type str or bytes.")
