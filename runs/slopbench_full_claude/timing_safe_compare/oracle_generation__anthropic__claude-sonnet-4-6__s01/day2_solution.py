import hmac


def timing_safe_compare(
    left: str | bytes,
    right: str | bytes,
    *,
    pad_to_length: int | None = None,
    pad_char: str = "\0",
) -> bool:
    """Compare two values in constant time.

    Both *left* and *right* must be the same type (str or bytes).
    Raises TypeError for any other type or when the types differ.

    When *pad_to_length* is given (integers only, for str inputs), both strings
    are right-padded with *pad_char* to that length before comparison.
    *pad_char* must be exactly one character.  Padding is silently skipped when
    the string is already at least as long as *pad_to_length*.
    """
    if not isinstance(left, (str, bytes)):
        raise TypeError(f"Expected str or bytes, got {type(left).__name__!r}")
    if not isinstance(right, (str, bytes)):
        raise TypeError(f"Expected str or bytes, got {type(right).__name__!r}")
    if type(left) is not type(right):
        raise TypeError(
            f"Both arguments must have the same type; "
            f"got {type(left).__name__!r} and {type(right).__name__!r}"
        )

    if pad_to_length is not None:
        if not isinstance(pad_to_length, int):
            raise TypeError(
                f"pad_to_length must be an int, got {type(pad_to_length).__name__!r}"
            )
        if not isinstance(pad_char, str) or len(pad_char) != 1:
            raise ValueError("pad_char must be a single character str")
        if not isinstance(left, str):
            raise TypeError("pad_to_length is only supported for str inputs")
        left = left.ljust(pad_to_length, pad_char)
        right = right.ljust(pad_to_length, pad_char)

    return hmac.compare_digest(left, right)
