from numbers import Real
from typing import Iterable


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    normalized_points = _normalize_points(points)
    _validate_window(start=start, end=end, interval=interval)

    ordered_points = sorted(normalized_points, key=lambda point: point[0])
    result: list[tuple[int, float | None]] = []

    point_index = 0
    current_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        while point_index < len(ordered_points) and ordered_points[point_index][0] <= timestamp:
            current_value = ordered_points[point_index][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result


def _validate_window(*, start: int, end: int, interval: int) -> None:
    if not _is_plain_int(start):
        raise TypeError("start must be an int")
    if not _is_plain_int(end):
        raise TypeError("end must be an int")
    if not _is_plain_int(interval):
        raise TypeError("interval must be an int")
    if interval <= 0:
        raise ValueError("interval must be greater than 0")
    if start > end:
        raise ValueError("start must be less than or equal to end")


def _normalize_points(points: list[tuple[int, float]]) -> list[tuple[int, float]]:
    if not isinstance(points, list):
        raise TypeError("points must be a list of (timestamp, value) tuples")

    normalized: list[tuple[int, float]] = []

    for index, point in enumerate(points):
        normalized.append(_normalize_point(point, index))

    return normalized


def _normalize_point(point: object, index: int) -> tuple[int, float]:
    if not isinstance(point, tuple) or len(point) != 2:
        raise TypeError(f"points[{index}] must be a (timestamp, value) tuple")

    timestamp, value = point

    if not _is_plain_int(timestamp):
        raise TypeError(f"points[{index}][0] must be an int timestamp")
    if not _is_plain_number(value):
        raise TypeError(f"points[{index}][1] must be a numeric value")

    return timestamp, float(value)


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_plain_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)
