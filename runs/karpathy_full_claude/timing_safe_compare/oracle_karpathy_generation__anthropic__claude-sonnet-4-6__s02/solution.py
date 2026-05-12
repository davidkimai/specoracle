import hmac


def timing_safe_compare(left: "str | bytes", right: "str | bytes") -> bool:
    if type(left) is not type(right):
        raise TypeError(
            f"Both arguments must have the same type, got {type(left).__name__} and {type(right).__name__}"
        )
    if not isinstance(left, (str, bytes)):
        raise TypeError(f"Arguments must be str or bytes, got {type(left).__name__}")
    return hmac.compare_digest(left, right)
