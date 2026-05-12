import hmac


def timing_safe_compare(left: "str | bytes", right: "str | bytes") -> bool:
    """Compare two values in constant time.

    Both *left* and *right* must be the same type (str or bytes).
    Raises TypeError if either argument is not str/bytes, or if the
    types differ.  Returns True only when the values are equal.
    """
    if not isinstance(left, (str, bytes)):
        raise TypeError(
            f"left must be str or bytes, not {type(left).__name__!r}"
        )
    if not isinstance(right, (str, bytes)):
        raise TypeError(
            f"right must be str or bytes, not {type(right).__name__!r}"
        )
    if type(left) is not type(right):
        raise TypeError(
            f"left and right must have the same type; "
            f"got {type(left).__name__!r} and {type(right).__name__!r}"
        )
    return hmac.compare_digest(left, right)
