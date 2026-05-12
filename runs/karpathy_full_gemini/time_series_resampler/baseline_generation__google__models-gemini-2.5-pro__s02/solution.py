"""A module for resampling time series data."""

from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Resamples a time series to a fixed interval using forward-fill.

    Generates a new series of points with timestamps from `start` to `end`
    (inclusive) at a fixed `interval`. The value for each new timestamp is
    determined by the value of the latest point in the input series at or
    before that timestamp (forward-fill). If no such point exists, the
    value is None.

    Args:
        points: A list of (timestamp, value) tuples. The list is not
            assumed to be sorted.
        start: The starting timestamp for the resampled series (inclusive).
        end: The ending timestamp for the resampled series (inclusive).
        interval: The interval between timestamps in the resampled series.

    Returns:
        A new list of (timestamp, value | None) tuples at the specified
        interval. Values are forward-filled. If no prior point exists for a
        given timestamp, the value is None.

    Raises:
        ValueError: If `interval` is not a positive integer.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    if start > end:
        return []

    # Sort points by timestamp to enable an efficient single-pass merge.
    # A copy is made to avoid modifying the caller's list.
    sorted_points = sorted(points, key=lambda p: p[0])

    resampled: list[tuple[int, float | None]] = []
    points_idx = 0
    num_points = len(sorted_points)
    last_known_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        # Advance through the sorted points to find the most recent value
        # at or before the current resampled timestamp.
        while (points_idx < num_points and
               sorted_points[points_idx][0] <= timestamp):
            last_known_value = sorted_points[points_idx][1]
            points_idx += 1

        resampled.append((timestamp, last_known_value))

    return resampled
