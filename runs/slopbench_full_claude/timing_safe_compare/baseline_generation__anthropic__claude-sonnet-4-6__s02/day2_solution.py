import hmac


def timing_safe_compare(
    left: str | bytes,
    right: str | bytes,
    pad_to_length: int | None = None,
    pad_char: str = "\0",
) -> bool:
    """Compare two values in constant time using hmac.compare_digest.

    Parameters
    ----------
    left:
        First value to compare. Must be str or bytes.
    right:
        Second value to compare. Must be str or bytes.
    pad_to_length:
        When set and both inputs are str, right-pad both strings to this
        length with *pad_char* before comparing. Ignored when inputs are
        bytes or when None.
    pad_char:
        Single character used for padding. Must be exactly one character.
        Defaults to the null character ``"\\0"``.

    Returns
    -------
    bool
        True if *left* and *right* are equal (after optional padding),
        False otherwise.

    Raises
    ------
    TypeError
        If either argument is not str or bytes, if the arguments have
        different types, or if *pad_char* is not a str.
    ValueError
        If *pad_char* is not exactly one character.
    """
    if not isinstance(left, (str, bytes)):
        raise TypeError(
            f"left must be str or bytes, got {type(left).__name__!r}"
        )
    if not isinstance(right, (str, bytes)):
        raise TypeError(
            f"right must be str or bytes, got {type(right).__name__!r}"
        )
    if type(left) is not type(right):
        raise TypeError(
            f"left and right must have the same type, got "
            f"{type(left).__name__!r} and {type(right).__name__!r}"
        )

    if pad_to_length is not None:
        if not isinstance(pad_char, str):
            raise TypeError(
                f"pad_char must be str, got {type(pad_char).__name__!r}"
            )
        if len(pad_char) != 1:
            raise ValueError(
                f"pad_char must be exactly one character, got {len(pad_char)}"
            )
        if isinstance(left, str):
            left = left.ljust(pad_to_length, pad_char)
            right = right.ljust(pad_to_length, pad_char)

    return hmac.compare_digest(left, right)
