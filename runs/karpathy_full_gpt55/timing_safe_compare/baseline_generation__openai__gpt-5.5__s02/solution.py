import hmac
from typing import Union, overload

__all__ = ["timing_safe_compare"]


@overload
def timing_safe_compare(left: str, right: str) -> bool:
    ...


@overload
def timing_safe_compare(left: bytes, right: bytes) -> bool:
    ...


def timing_safe_compare(left: Union[str, bytes], right: Union[str, bytes]) -> bool:
    if not isinstance(left, (str, bytes)):
        raise TypeError("left must be str or bytes")
    if not isinstance(right, (str, bytes)):
        raise TypeError("right must be str or bytes")
    if type(left) is not type(right):
        raise TypeError("left and right must have the same type")

    return hmac.compare_digest(left, right)
