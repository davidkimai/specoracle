from __future__ import annotations

import hmac


def timing_safe_compare(
    left: str | bytes,
    right: str | bytes,
    pad_to_length: int | None = None,
    pad_char: str = "\0",
) -> bool:
    if not isinstance(left, (str, bytes)) or not isinstance(right, (str, bytes)):
        raise TypeError("values must be str or bytes")
    if type(left) is not type(right):
        raise TypeError("values must share a type")
    if pad_to_length is not None:
        if not isinstance(pad_char, str) or len(pad_char) != 1:
            raise TypeError("pad_char must be exactly one character")
        if isinstance(left, str):
            left = left.ljust(pad_to_length, pad_char)
            right = right.ljust(pad_to_length, pad_char)
    return hmac.compare_digest(left, right)
