import hmac
from typing import Union

Comparable = Union[str, bytes]


def timing_safe_compare(left: Comparable, right: Comparable) -> bool:
    if type(left) not in (str, bytes):
        raise TypeError("left must be str or bytes")
    if type(right) not in (str, bytes):
        raise TypeError("right must be str or bytes")
    if type(left) is not type(right):
        raise TypeError("left and right must have the same type")
    return hmac.compare_digest(left, right)
