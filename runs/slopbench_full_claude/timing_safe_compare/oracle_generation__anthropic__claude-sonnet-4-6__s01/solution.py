import hmac


def timing_safe_compare(left: str | bytes, right: str | bytes) -> bool:
    """Compare two values in constant time.

    Both *left* and *right* must be the same type (str or bytes).
    Raises TypeError for any other type or when the types differ.
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
    return hmac.compare_digest(left, right)
