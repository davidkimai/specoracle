from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]], *, start: int, end: int, interval: int
) -> list[tuple[int, float | None]]:
    """Resample points onto a regular timestamp grid using forward fill.

    Assumptions:
    - interval must be positive.
    - points may be unsorted.
    - when multiple points have the same timestamp, the later input point wins.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    ordered_points = sorted(enumerate(points), key=lambda item: (item[1][0], item[0]))

    result: list[tuple[int, float | None]] = []
    point_index = 0
    current_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        while (
            point_index < len(ordered_points)
            and ordered_points[point_index][1][0] <= timestamp
        ):
            current_value = ordered_points[point_index][1][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result
