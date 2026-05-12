import hmac
from typing import Union

Comparable = Union[str, bytes]


def _is_supported(value: object) -> bool:
    return isinstance(value, (str, bytes))


def timing_safe_compare(left: Comparable, right: Comparable) -> bool:
    if not _is_supported(left):
        raise TypeError("left must be str or bytes")
    if not _is_supported(right):
        raise TypeError("right must be str or bytes")
    if type(left) is not type(right):
        raise TypeError("left and right must have the same type")

    return hmac.compare_digest(left, right)
