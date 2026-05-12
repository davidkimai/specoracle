def resample_series(
    points: list[tuple[int, float]], *, start: int, end: int, interval: int
) -> list[tuple[int, float | None]]:
    """Resample timestamped points onto a regular grid using forward fill."""
    if interval <= 0:
        raise ValueError("interval must be positive")

    ordered_points = sorted(points, key=lambda point: point[0])
    result: list[tuple[int, float | None]] = []
    point_index = 0
    current_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        while (
            point_index < len(ordered_points)
            and ordered_points[point_index][0] <= timestamp
        ):
            current_value = ordered_points[point_index][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result
