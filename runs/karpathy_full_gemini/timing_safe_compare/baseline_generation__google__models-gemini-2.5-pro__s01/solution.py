import hmac
from typing import Union

__all__ = ['timing_safe_compare']


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    """
    Compare two strings or byte strings in constant time.

    This function is a typed wrapper around hmac.compare_digest to help
    prevent timing attacks. It ensures that both inputs are of the same type
    (either str or bytes) before comparison.

    Args:
        left: The first string or byte string to compare.
        right: The second string or byte string to compare.

    Returns:
        True if the inputs are equal, False otherwise.

    Raises:
        TypeError: If the inputs are not both str or both bytes, or if their
                   types are mismatched.
    """
    if type(left) is not type(right):
        raise TypeError("Both inputs must have the same type.")

    left_for_compare: bytes
    right_for_compare: bytes

    if isinstance(left, str):
        # The type check above ensures `right` is also a str.
        left_for_compare = left.encode('utf-8')
        right_for_compare = right.encode('utf-8')
    elif isinstance(left, bytes):
        # The type check ensures `right` is also bytes.
        left_for_compare = left
        right_for_compare = right
    else:
        raise TypeError("Inputs must be str or bytes.")

    return hmac.compare_digest(left_for_compare, right_for_compare)
