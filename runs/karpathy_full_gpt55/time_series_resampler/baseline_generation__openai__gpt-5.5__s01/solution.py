def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """
    Resample a timestamped series onto a regular grid using forward fill.

    For each timestamp from ``start`` to ``end`` inclusive, stepping by
    ``interval``, the returned value is the value from the input point with the
    greatest timestamp less than or equal to that grid timestamp. If no such
    point exists, the value is None.

    Input points do not need to be sorted. If multiple input points have the
    same timestamp, the one appearing latest in the input list is used.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    if start > end:
        return []

    indexed_points = sorted(
        ((timestamp, index, value) for index, (timestamp, value) in enumerate(points)),
        key=lambda item: (item[0], item[1]),
    )

    result: list[tuple[int, float | None]] = []
    point_index = 0
    current_value: float | None = None
    point_count = len(indexed_points)

    timestamp = start
    while timestamp <= end:
        while point_index < point_count and indexed_points[point_index][0] <= timestamp:
            current_value = indexed_points[point_index][2]
            point_index += 1

        result.append((timestamp, current_value))
        timestamp += interval

    return result
