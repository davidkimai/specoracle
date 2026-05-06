import hmac


def timing_safe_compare(
    left: str | bytes,
    right: str | bytes,
    pad_to_length: int | None = None,
    pad_char: str = "\0",
) -> bool:
    """Compare two values in constant time.

    Both arguments must be the same type (str or bytes).
    Raises TypeError for unsupported or mismatched types.

    When pad_to_length is set and both arguments are str, right-pad both
    strings to that length with pad_char before comparing.
    pad_char must be exactly one character; raises ValueError otherwise.
    pad_to_length is ignored (and not validated against type) when inputs
    are bytes, to preserve original behavior.
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

    if pad_to_length is not None and isinstance(left, str):
        if not isinstance(pad_char, str) or len(pad_char) != 1:
            raise ValueError(
                f"pad_char must be a single character str, got {pad_char!r}"
            )
        left = left.ljust(pad_to_length, pad_char)
        right = right.ljust(pad_to_length, pad_char)

    return hmac.compare_digest(left, right)
