import hmac
from typing import Union

Comparable = Union[str, bytes]


def _require_str_or_bytes(name: str, value: object) -> type:
    value_type = type(value)
    if value_type not in (str, bytes):
        raise TypeError(f"{name} must be str or bytes, not {value_type.__name__}")
    return value_type


def timing_safe_compare(left: Comparable, right: Comparable) -> bool:
    left_type = _require_str_or_bytes("left", left)
    right_type = _require_str_or_bytes("right", right)

    if left_type is not right_type:
        raise TypeError("left and right must have the same type")

    return hmac.compare_digest(left, right)
