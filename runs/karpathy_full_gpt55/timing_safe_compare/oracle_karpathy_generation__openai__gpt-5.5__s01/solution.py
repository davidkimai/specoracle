import hmac


def timing_safe_compare(left: str | bytes, right: str | bytes) -> bool:
    if not isinstance(left, (str, bytes)) or not isinstance(right, (str, bytes)):
        raise TypeError("inputs must be str or bytes")
    if type(left) is not type(right):
        raise TypeError("inputs must have the same type")
    if isinstance(left, str):
        return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))
    return hmac.compare_digest(left, right)
