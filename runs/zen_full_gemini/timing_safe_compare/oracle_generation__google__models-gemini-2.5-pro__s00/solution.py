# timing_safe_compare.py

"""A module for timing-safe string comparison."""

import hmac
from typing import Union

__all__ = ["timing_safe_compare"]

Comparable = Union[str, bytes]


def _validate_types(left: Comparable, right: Comparable) -> None:
    """
    Ensures that both inputs are of the same supported type (str or bytes).

    Args:
        left: The first value.
        right: The second value.

    Raises:
        TypeError: If types are mismatched or not str/bytes.
    """
    if type(left) is not type(right):
        raise TypeError(
            "Mismatched types for comparison: "
            f"got {type(left).__name__} and {type(right).__name__}"
        )

    if not isinstance(left, (str, bytes)):
        # Since types are guaranteed to be the same, we only need to check one.
        raise TypeError(f"Unsupported type for comparison: {type(left).__name__}")


def _to_bytes(value: Comparable) -> bytes:
    """
    Encodes a string to bytes or passes bytes through.

    Args:
        value: The string or bytes value.

    Returns:
        The value as a byte string, UTF-8 encoded if it was a string.
    """
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def timing_safe_compare(left: Comparable, right: Comparable) -> bool:
    """
    Compares two strings or byte strings in a way that is safe against
    timing attacks.

    Both inputs must be of the same type, either `str` or `bytes`.

    This function is a wrapper around `hmac.compare_digest`.

    Args:
        left: The first string or byte string to compare.
        right: The second string or byte string to compare.

    Returns:
        True if the inputs are equal, False otherwise.

    Raises:
        TypeError: If the inputs are not both of type `str` or both of type
                   `bytes`.
    """
    _validate_types(left, right)

    # hmac.compare_digest requires bytes. The helper function handles
    # the potential conversion from str.
    left_bytes = _to_bytes(left)
    right_bytes = _to_bytes(right)

    return hmac.compare_digest(left_bytes, right_bytes)
