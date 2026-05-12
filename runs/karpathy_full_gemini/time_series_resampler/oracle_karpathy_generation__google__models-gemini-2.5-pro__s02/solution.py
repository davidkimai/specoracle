"""A module for resampling time series data."""

from typing import List, Optional, Tuple


def resample_series(
    points: List[Tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> List[Tuple[int, Optional[float]]]:
    """Resamples a time series to a fixed interval using forward-fill.

    Returns timestamps from `start` to `end` inclusive by `interval`. The value
    for each timestamp is determined by forward-filling from the latest point
    in `points` that occurred at or before the timestamp. If no such point
    exists, the value is `None`.

    Args:
        points: A list of (timestamp, value) tuples. Not assumed to be sorted.
        start: The start timestamp of the resampled series (inclusive).
        end: The end timestamp of the resampled series (inclusive).
        interval: The interval between timestamps in the resampled series.

    Returns:
        A new list of (timestamp, value) tuples for the resampled series.

    Raises:
        ValueError: If `interval` is not a positive integer.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    if start > end:
        return []

    if not points:
        return [(t, None) for t in range(start, end + 1, interval)]

    # Sort points by timestamp to enable an efficient single-pass scan.
    # The default tuple sort is by the first element, which is the timestamp.
    sorted_points = sorted(points)

    result: List[Tuple[int, Optional[float]]] = []
    points_idx = 0
    last_known_value: Optional[float] = None

    for t in range(start, end + 1, interval):
        # Advance the pointer through sorted_points to find the latest value
        # at or before the current timestamp `t`.
        while (
            points_idx < len(sorted_points)
            and sorted_points[points_idx][0] <= t
        ):
            last_known_value = sorted_points[points_idx][1]
            points_idx += 1

        result.append((t, last_known_value))

    return result
