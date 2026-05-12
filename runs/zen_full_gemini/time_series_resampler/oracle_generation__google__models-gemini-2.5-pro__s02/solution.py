"""A module for resampling time series data using forward-fill."""


def _validate_resample_parameters(start: int, end: int, interval: int) -> None:
    """
    Checks if the resampling parameters are valid.

    Args:
        start: The start timestamp of the resampled series.
        end: The end timestamp of the resampled series.
        interval: The interval between timestamps in the resampled series.

    Raises:
        ValueError: If `start` is after `end` or `interval` is not positive.
    """
    if start > end:
        raise ValueError("start must not be after end")
    if interval <= 0:
        raise ValueError("interval must be positive")


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """
    Resamples a time series to a fixed interval using forward-fill.

    This function generates a new series of data points at regular timestamps
    starting from `start` up to `end` (inclusive), with a step of `interval`.
    The value for each new timestamp is determined by the "last observation
    carried forward" method: it's the value of the latest point in the
    original series with a timestamp less than or equal to the new timestamp.
    If no such point exists (i.e., for timestamps before the first point in
    the original series), the value is `None`.

    Args:
        points: A list of (timestamp, value) tuples representing the original
                time series. The list does not need to be sorted.
        start: The start timestamp for the new, resampled series (inclusive).
        end: The end timestamp for the new, resampled series (inclusive).
        interval: The time interval between consecutive points in the new series.

    Returns:
        A new list of (timestamp, value) tuples at the specified interval.
        Values are forward-filled, or `None` if no preceding data is available.

    Raises:
        ValueError: If `start` > `end` or `interval` is not positive.
    """
    _validate_resample_parameters(start, end, interval)

    # Sort the input points by timestamp to enable a single-pass algorithm.
    # A copy is created to avoid mutating the caller's list.
    sorted_points = sorted(points, key=lambda p: p[0])

    # Use an iterator for efficient, stateful consumption of the sorted points.
    points_iter = iter(sorted_points)
    next_point = next(points_iter, None)

    resampled_points: list[tuple[int, float | None]] = []
    last_known_value: float | None = None

    for target_timestamp in range(start, end + 1, interval):
        # Advance through the source points as long as they are at or before
        # the current target timestamp. The value of the last such point is
        # what we'll carry forward.
        while next_point and next_point[0] <= target_timestamp:
            last_known_value = next_point[1]
            next_point = next(points_iter, None)

        resampled_points.append((target_timestamp, last_known_value))

    return resampled_points
