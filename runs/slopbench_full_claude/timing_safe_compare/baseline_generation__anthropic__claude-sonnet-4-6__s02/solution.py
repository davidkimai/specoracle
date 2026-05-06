import hmac


def timing_safe_compare(left: str | bytes, right: str | bytes) -> bool:
    """Compare two values in constant time using hmac.compare_digest.

    Parameters
    ----------
    left:
        First value to compare. Must be str or bytes.
    right:
        Second value to compare. Must be str or bytes.

    Returns
    -------
    bool
        True if *left* and *right* are equal, False otherwise.

    Raises
    ------
    TypeError
        If either argument is not str or bytes, or if the arguments have
        different types.
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
    return hmac.compare_digest(left, right)
