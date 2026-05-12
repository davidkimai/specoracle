from __future__ import annotations

from typing import Optional


__all__ = ["resample_series"]


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, Optional[float]]]:
    """
    Resample a time series onto a regular timestamp grid using forward-fill.

    For each timestamp from ``start`` to ``end`` inclusive, stepping by
    ``interval``, the returned value is the value from the latest input point
    whose timestamp is less than or equal to that grid timestamp. If no such
    point exists, the value is ``None``.

    Input points may be unsorted. If multiple points have the same timestamp,
    their original input order is preserved, so the last such point in the input
    is used for forward-filling.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    if start > end:
        return []

    sorted_points = sorted(points, key=lambda point: point[0])

    result: list[tuple[int, Optional[float]]] = []
    point_index = 0
    point_count = len(sorted_points)
    current_value: Optional[float] = None

    for timestamp in range(start, end + 1, interval):
        while (
            point_index < point_count
            and sorted_points[point_index][0] <= timestamp
        ):
            current_value = sorted_points[point_index][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result
