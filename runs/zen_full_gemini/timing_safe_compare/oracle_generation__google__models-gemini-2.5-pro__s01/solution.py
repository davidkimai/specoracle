"""
A module for timing-safe string and byte comparison.

This module provides a typed wrapper around hmac.compare_digest to ensure
that comparisons are performed in a way that helps mitigate timing attacks.
"""

import hmac
from typing import Any

__all__ = ["timing_safe_compare"]


def timing_safe_compare(left: Any, right: Any) -> bool:
    """
    Performs a timing-safe comparison of two strings or byte strings.

    This function is a wrapper around hmac.compare_digest to provide
    stricter type checking. Both inputs must be of the same type, either
    str or bytes.

    Args:
        left: The left-hand value to compare. Must be str or bytes.
        right: The right-hand value to compare. Must be str or bytes.

    Returns:
        True if the values are equal, False otherwise.

    Raises:
        TypeError: If the inputs are not of the same type, or if their
                   type is not str or bytes.
    """
    if type(left) is not type(right):
        raise TypeError("Arguments must have the same type (both str or both bytes).")

    if not isinstance(left, (str, bytes)):
        raise TypeError("Arguments must be of type str or bytes.")

    # At this point, we know both `left` and `right` are of the same supported
    # type (either str or bytes). We now prepare them for hmac.compare_digest,
    # which requires bytes.

    if isinstance(left, str):
        # If one is a string, the other must also be a string.
        # Encode both to bytes using a standard, unambiguous encoding.
        left_for_compare = left.encode("utf-8")
        right_for_compare = right.encode("utf-8")
    else:
        # The values must already be bytes.
        left_for_compare = left
        right_for_compare = right

    return hmac.compare_digest(left_for_compare, right_for_compare)
