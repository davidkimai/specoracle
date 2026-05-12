def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    if attempts < 0:
        raise ValueError(f"attempts must be non-negative, got {attempts}")
    if base_seconds <= 0:
        raise ValueError(f"base_seconds must be positive, got {base_seconds}")
    if cap_seconds <= 0:
        raise ValueError(f"cap_seconds must be positive, got {cap_seconds}")

    return [min(base_seconds * (2 ** i), cap_seconds) for i in range(attempts)]


def next_allowed_times(start_timestamp: int, schedule: list[int]) -> list[int]:
    times = []
    current = start_timestamp
    for delay in schedule:
        current += delay
        times.append(current)
    return times
