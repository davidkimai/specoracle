from __future__ import annotations

import hmac
from typing import overload

__all__ = ["timing_safe_compare"]


@overload
def timing_safe_compare(left: str, right: str) -> bool:
    ...


@overload
def timing_safe_compare(left: bytes, right: bytes) -> bool:
    ...


def timing_safe_compare(left: str | bytes, right: str | bytes) -> bool:
    """
    Compare two str or bytes values using hmac.compare_digest.

    Both arguments must be exactly the same supported type: str with str, or
    bytes with bytes. Unsupported types or mixed types raise TypeError.
    """
    left_type = type(left)
    right_type = type(right)

    if left_type not in (str, bytes) or right_type not in (str, bytes):
        raise TypeError("timing_safe_compare arguments must be str or bytes")

    if left_type is not right_type:
        raise TypeError("timing_safe_compare arguments must have the same type")

    return hmac.compare_digest(left, right)
