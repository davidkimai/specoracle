from __future__ import annotations

from numbers import Real

__all__ = ["resample_series"]


Point = tuple[int, float]
ResampledPoint = tuple[int, float | None]


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_real_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _validate_integer(name: str, value: object) -> int:
    if not _is_plain_int(value):
        raise TypeError(f"{name} must be an int")
    return value


def _validate_bounds(start: object, end: object, interval: object) -> tuple[int, int, int]:
    checked_start = _validate_integer("start", start)
    checked_end = _validate_integer("end", end)
    checked_interval = _validate_integer("interval", interval)

    if checked_interval <= 0:
        raise ValueError("interval must be greater than 0")
    if checked_start > checked_end:
        raise ValueError("start must be less than or equal to end")

    return checked_start, checked_end, checked_interval


def _normalize_points(points: list[tuple[int, float]]) -> list[Point]:
    if not isinstance(points, list):
        raise TypeError("points must be a list of (timestamp, value) tuples")

    normalized: list[Point] = []

    for index, point in enumerate(points):
        if not isinstance(point, tuple) or len(point) != 2:
            raise TypeError(f"points[{index}] must be a (timestamp, value) tuple")

        timestamp, value = point

        if not _is_plain_int(timestamp):
            raise TypeError(f"points[{index}][0] must be an int timestamp")
        if not _is_real_number(value):
            raise TypeError(f"points[{index}][1] must be a real number")

        normalized.append((timestamp, float(value)))

    return sorted(normalized, key=lambda item: item[0])


def _target_timestamps(start: int, end: int, interval: int) -> list[int]:
    timestamps: list[int] = []
    timestamp = start

    while timestamp <= end:
        timestamps.append(timestamp)
        timestamp += interval

    return timestamps


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    checked_start, checked_end, checked_interval = _validate_bounds(start, end, interval)
    sorted_points = _normalize_points(points)

    result: list[ResampledPoint] = []
    point_index = 0
    current_value: float | None = None

    for timestamp in _target_timestamps(checked_start, checked_end, checked_interval):
        while point_index < len(sorted_points) and sorted_points[point_index][0] <= timestamp:
            current_value = sorted_points[point_index][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result
