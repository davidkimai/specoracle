def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    if base_seconds <= 0:
        raise ValueError("base_seconds must be positive")
    if cap_seconds <= 0:
        raise ValueError("cap_seconds must be positive")
    
    schedule = []
    delay = base_seconds
    for _ in range(attempts):
        schedule.append(min(delay, cap_seconds))
        delay *= 2
    return schedule
