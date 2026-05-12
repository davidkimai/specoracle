def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list:
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")
    result = []
    for i in range(attempts):
        delay = base_seconds * (2 ** i)
        result.append(min(delay, cap_seconds))
    return result
