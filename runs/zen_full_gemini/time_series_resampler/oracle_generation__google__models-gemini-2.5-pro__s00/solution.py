"""
A module for resampling time series data using forward-fill.
"""

import typing


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Resamples a time series using a forward-fill strategy.

    This function generates a new series of timestamps from `start` to `end`
    (inclusive) at a fixed `interval`. For each new timestamp, the corresponding
    value is determined by the last seen value from the input `points` at or
    before that timestamp. If no point has occurred yet, the value is `None`.

    Args:
        points: A list of (timestamp, value) tuples representing the
                original time series. The list does not need to be sorted.
        start: The starting timestamp for the new series (inclusive).
        end: The ending timestamp for the new series (inclusive).
        interval: The step between timestamps in the new series.

    Returns:
        A new list of (timestamp, value | None) tuples for the resampled series.

    Raises:
        ValueError: If `interval` is not a positive integer.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    # To efficiently find the latest point, we first sort the input points
    # by timestamp. A copy is made to avoid mutating the original list.
    sorted_points = sorted(points)

    resampled_points = []
    points_iterator = iter(sorted_points)
    
    # Get the first point from the iterator to begin the process.
    current_point = next(points_iterator, None)
    last_known_value: float | None = None

    # Iterate through each target timestamp in the desired range.
    for timestamp in range(start, end + 1, interval):
        # Advance through the sorted points to update the last known value.
        # We process all points that occur at or before the current target
        # timestamp. The stable nature of sorted() ensures that if multiple
        # points share a timestamp, the one later in the original list is used.
        while current_point is not None and current_point[0] <= timestamp:
            last_known_value = current_point[1]
            current_point = next(points_iterator, None)
        
        resampled_points.append((timestamp, last_known_value))

    return resampled_points
