from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Resample a time series using forward-fill semantics."""
    _validate_resample_bounds(start, end, interval)
    normalized_points = _normalize_points(points)

    result: list[tuple[int, float | None]] = []
    point_index = 0
    current_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        while (
            point_index < len(normalized_points)
            and normalized_points[point_index][0] <= timestamp
        ):
            current_value = normalized_points[point_index][1]
            point_index += 1

        result.append((timestamp, current_value))

    return result


def _validate_resample_bounds(start: int, end: int, interval: int) -> None:
    if not _is_int(start):
        raise TypeError("start must be an int")
    if not _is_int(end):
        raise TypeError("end must be an int")
    if not _is_int(interval):
        raise TypeError("interval must be an int")
    if interval <= 0:
        raise ValueError("interval must be greater than zero")
    if start > end:
        raise ValueError("start must be less than or equal to end")


def _normalize_points(points: list[tuple[int, float]]) -> list[tuple[int, float]]:
    if not isinstance(points, list):
        raise TypeError("points must be a list of (timestamp, value) tuples")

    normalized: list[tuple[int, float]] = []

    for index, point in enumerate(points):
        if not isinstance(point, tuple) or len(point) != 2:
            raise TypeError(f"points[{index}] must be a tuple of (int, float)")

        timestamp, value = point

        if not _is_int(timestamp):
            raise TypeError(f"points[{index}][0] must be an int")
        if not _is_number(value):
            raise TypeError(f"points[{index}][1] must be a float")

        normalized.append((timestamp, float(value)))

    return sorted(normalized, key=lambda item: item[0])


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
