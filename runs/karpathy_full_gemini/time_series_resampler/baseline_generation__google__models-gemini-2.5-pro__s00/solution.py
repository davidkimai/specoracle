"""A module for resampling time series data."""


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Resamples a time series using forward-fill.

    Generates timestamps from 'start' to 'end' inclusive, with a step of
    'interval'. For each generated timestamp, the value is determined by the
    latest point in the input series at or before that timestamp. If no such
    point exists, the value is None.

    Args:
        points: A list of (timestamp, value) tuples. The list is not
                assumed to be sorted.
        start: The starting timestamp for the resampled series (inclusive).
        end: The ending timestamp for the resampled series (inclusive).
        interval: The interval between timestamps in the resampled series.

    Returns:
        A new list of (timestamp, value | None) tuples, sorted by timestamp.

    Raises:
        ValueError: If 'interval' is not positive.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    # To enable an efficient single-pass algorithm, sort the input points
    # by timestamp. A copy is sorted to avoid modifying the caller's list.
    sorted_points = sorted(points)

    resampled_data: list[tuple[int, float | None]] = []
    points_idx = 0
    num_points = len(sorted_points)
    last_known_value: float | None = None

    # Iterate through the target timestamps.
    for timestamp in range(start, end + 1, interval):
        # Advance through the sorted source data, updating the last_known_value
        # as we pass points that occurred at or before the current target
        # timestamp.
        while (points_idx < num_points and
               sorted_points[points_idx][0] <= timestamp):
            last_known_value = sorted_points[points_idx][1]
            points_idx += 1

        # The last_known_value is now the correct forward-filled value for
        # the current timestamp.
        resampled_data.append((timestamp, last_known_value))

    return resampled_data
