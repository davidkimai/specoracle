import hmac


def timing_safe_compare(
    left: str | bytes,
    right: str | bytes,
    pad_to_length: int | None = None,
    pad_char: str = "\0",
) -> bool:
    if type(left) is not type(right):
        raise TypeError(
            f"Both arguments must have the same type, got {type(left).__name__!r} and {type(right).__name__!r}"
        )
    if not isinstance(left, (str, bytes)):
        raise TypeError(
            f"Arguments must be str or bytes, got {type(left).__name__!r}"
        )
    if pad_to_length is not None:
        if not isinstance(left, str):
            raise TypeError(
                "pad_to_length is only supported for str arguments"
            )
        if len(pad_char) != 1:
            raise ValueError(
                f"pad_char must be exactly one character, got {pad_char!r}"
            )
        left = left.ljust(pad_to_length, pad_char)
        right = right.ljust(pad_to_length, pad_char)
    return hmac.compare_digest(left, right)
