"""
A module for resampling time series data.
"""

import typing


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Resamples a time series using forward-fill logic.

    Generates a new series of points at regular intervals from a start to an
    end time. The value for each new point is determined by the last known
    value from the input series at or before the new point's timestamp.

    For example:
        resample_series(
            points=[(0, 0.0), (10, 1.0), (25, 2.5)],
            start=5,
            end=26,
            interval=10
        )
    returns:
        [(5, 0.0), (15, 1.0), (25, 2.5)]

    Args:
        points: A list of (timestamp, value) tuples. The list does not
                need to be sorted.
        start: The timestamp for the first point in the resampled series.
        end: The timestamp for the last possible point in the resampled series.
        interval: The time difference between consecutive points in the
                  resampled series.

    Returns:
        A new list of (timestamp, value) tuples, sorted by timestamp,
        representing the resampled series. If no value is known for a given
        timestamp (i.e., no input point occurs at or before it), the value
        will be None.

    Raises:
        ValueError: If `interval` is not a positive integer.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    # Sort points by timestamp to enable efficient one-pass processing.
    # A copy is made so the original list is not modified.
    sorted_points = sorted(points)

    resampled_points: list[tuple[int, float | None]] = []
    points_idx = 0
    num_points = len(sorted_points)
    last_known_value: float | None = None

    for t_target in range(start, end + 1, interval):
        # Advance through sorted_points to find the last value at or before
        # the current target timestamp. Since both t_target and the points'
        # timestamps are increasing, we can do this in a single pass.
        while (
            points_idx < num_points
            and sorted_points[points_idx][0] <= t_target
        ):
            last_known_value = sorted_points[points_idx][1]
            points_idx += 1

        resampled_points.append((t_target, last_known_value))

    return resampled_points
