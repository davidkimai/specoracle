import hmac


def timing_safe_compare(left: "str | bytes", right: "str | bytes") -> bool:
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
            f"left and right must have the same type; "
            f"got {type(left).__name__!r} and {type(right).__name__!r}"
        )
    return hmac.compare_digest(left, right)
