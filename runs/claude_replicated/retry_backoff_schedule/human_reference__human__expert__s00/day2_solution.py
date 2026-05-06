def build_retry_schedule(attempts: int, base_seconds: int, cap_seconds: int) -> list[int]:
    if attempts < 0 or base_seconds <= 0 or cap_seconds <= 0:
        raise ValueError("invalid backoff parameters")
    schedule = []
    delay = base_seconds
    for _ in range(attempts):
        schedule.append(min(delay, cap_seconds))
        delay *= 2
    return schedule


def next_allowed_times(start_timestamp: int, schedule: list[int]) -> list[int]:
    times = []
    current = start_timestamp
    for delay in schedule:
        current += delay
        times.append(current)
    return times
