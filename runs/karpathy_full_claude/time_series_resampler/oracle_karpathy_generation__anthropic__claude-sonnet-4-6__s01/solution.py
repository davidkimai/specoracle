def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    sorted_points = sorted(points, key=lambda p: p[0])
    result = []
    ts = start
    while ts <= end:
        value = None
        for t, v in sorted_points:
            if t <= ts:
                value = v
            else:
                break
        result.append((ts, value))
        ts += interval
    return result
