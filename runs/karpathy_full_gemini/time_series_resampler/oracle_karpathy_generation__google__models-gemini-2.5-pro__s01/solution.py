"""
Provides a function to resample time series data to a fixed interval.
"""

def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int
) -> list[tuple[int, float | None]]:
    """
    Resamples a time series to a fixed interval using forward-fill.

    The input `points` list is not assumed to be sorted. The function generates
    a new series of timestamps from `start` to `end` (inclusive) with a
    step of `interval`. For each new timestamp, the value is determined by
    the most recent point in the input series at or before that timestamp.
    If no such point exists, the value is None.

    Args:
        points: A list of (timestamp, value) tuples representing the
                original time series data.
        start: The start timestamp for the resampled series (inclusive).
        end: The end timestamp for the resampled series (inclusive).
        interval: The interval between timestamps in the resampled series.

    Returns:
        A new list of (timestamp, value | None) tuples at the specified
        interval, with values forward-filled.

    Raises:
        ValueError: If `interval` is not a positive integer.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    # Sort points by timestamp to enable an efficient single-pass merge.
    # A copy is made so the original list is not modified.
    sorted_points = sorted(points, key=lambda p: p[0])

    resampled_points: list[tuple[int, float | None]] = []
    points_idx = 0
    num_points = len(sorted_points)
    last_value: float | None = None

    # `range` naturally handles the case where start > end by producing
    # an empty sequence, resulting in an empty list being returned.
    for t in range(start, end + 1, interval):
        # Advance through sorted_points to find the latest value for
        # the current timestamp `t`.
        while (points_idx < num_points and
               sorted_points[points_idx][0] <= t):
            last_value = sorted_points[points_idx][1]
            points_idx += 1

        resampled_points.append((t, last_value))

    return resampled_points
