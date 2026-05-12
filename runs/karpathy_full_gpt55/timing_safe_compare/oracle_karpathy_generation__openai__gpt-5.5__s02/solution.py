import hmac


def timing_safe_compare(left: str | bytes, right: str | bytes) -> bool:
    if type(left) is not type(right):
        raise TypeError("left and right must have the same type")
    if type(left) not in (str, bytes):
        raise TypeError("left and right must be str or bytes")
    return hmac.compare_digest(left, right)
