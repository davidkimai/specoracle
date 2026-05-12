from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """
    Resample timestamped points onto a regular grid using forward-fill.

    The returned timestamps are start, start + interval, ... up to and including
    end when end falls on the interval grid. Each output value is the value from
    the latest input point with timestamp less than or equal to the output
    timestamp, or None if no such point exists.

    If multiple input points have the same timestamp, the last one in the input
    order is used for that timestamp.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    ordered_points = sorted(points, key=lambda point: point[0])

    result: list[tuple[int, float | None]] = []
    point_index = 0
    point_count = len(ordered_points)
    current_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        while point_index < point_count and ordered_points[point_index][0] <= timestamp:
            current_value = ordered_points[point_index][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result
