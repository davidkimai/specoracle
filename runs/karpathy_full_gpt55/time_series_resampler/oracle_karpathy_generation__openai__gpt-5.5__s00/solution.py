def resample_series(
    points: list[tuple[int, float]], *, start: int, end: int, interval: int
) -> list[tuple[int, float | None]]:
    if interval <= 0:
        raise ValueError("interval must be positive")

    ordered = sorted(points, key=lambda point: point[0])
    result: list[tuple[int, float | None]] = []

    index = 0
    value: float | None = None

    for timestamp in range(start, end + 1, interval):
        while index < len(ordered) and ordered[index][0] <= timestamp:
            value = ordered[index][1]
            index += 1
        result.append((timestamp, value))

    return result
