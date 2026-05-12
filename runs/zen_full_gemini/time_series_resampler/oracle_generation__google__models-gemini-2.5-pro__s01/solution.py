#
# A module for resampling time series data.
#
# The primary entry point is `resample_series`, which implements a
# forward-fill resampling strategy for a series of timestamped data points.
#

def _validate_inputs(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> None:
    """Checks if the inputs for resampling are valid."""
    if not isinstance(start, int):
        raise TypeError("start must be an integer.")
    if not isinstance(end, int):
        raise TypeError("end must be an integer.")
    if not isinstance(interval, int):
        raise TypeError("interval must be an integer.")

    if interval <= 0:
        raise ValueError("interval must be a positive integer.")
    if start > end:
        raise ValueError("start cannot be after end.")

    if not isinstance(points, list):
        raise TypeError("points must be a list.")

    for i, point in enumerate(points):
        if not (
            isinstance(point, tuple)
            and len(point) == 2
            and isinstance(point[0], int)
            and isinstance(point[1], (int, float))
        ):
            raise TypeError(
                f"Element at index {i} in points is not a valid (int, float) tuple."
            )


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """
    Resamples a time series to a fixed interval using forward-fill.

    The function generates timestamps from `start` to `end` inclusive, with a
    step of `interval`. For each generated timestamp, it finds the value from
    the latest point in the input `points` that occurred at or before that
    timestamp. If no such point exists, the value is `None`.

    Args:
        points: A list of (timestamp, value) tuples. The list is not
                assumed to be sorted.
        start: The starting timestamp for the resampled series (inclusive).
        end: The ending timestamp for the resampled series (inclusive).
        interval: The interval between timestamps in the resampled series.

    Returns:
        A new list of (timestamp, value | None) tuples at the specified
        interval, with values determined by forward-fill.

    Raises:
        ValueError: If `interval` is not positive or if `start` is after `end`.
        TypeError: If inputs have incorrect types.
    """
    _validate_inputs(points=points, start=start, end=end, interval=interval)

    # Sort points by timestamp to enable efficient forward-filling.
    # A copy is made to avoid mutating the caller's list.
    sorted_points = sorted(points, key=lambda p: p[0])

    resampled_points: list[tuple[int, float | None]] = []
    points_idx = 0
    num_points = len(sorted_points)
    last_known_value: float | None = None

    for timestamp in range(start, end + 1, interval):
        # Advance through sorted_points to find the last value at or before
        # the current target timestamp.
        while points_idx < num_points and sorted_points[points_idx][0] <= timestamp:
            last_known_value = float(sorted_points[points_idx][1])
            points_idx += 1

        resampled_points.append((timestamp, last_known_value))

    return resampled_points
