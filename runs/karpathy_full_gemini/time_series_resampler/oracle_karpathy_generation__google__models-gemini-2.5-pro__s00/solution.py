# time_series_resampler.py

from __future__ import annotations

def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int
) -> list[tuple[int, float | None]]:
    """Resamples a time series to a fixed interval using forward-fill.

    Generates a new series of points with timestamps from `start` to `end`
    (inclusive) at a fixed `interval`. The value for each new timestamp is
    determined by taking the value from the latest point in the input series
    that has a timestamp less than or equal to the new timestamp (forward-fill).
    If no such point exists (i.e., the new timestamp is before the first
    timestamp in the input series), the value is None.

    Args:
        points: A list of (timestamp, value) tuples representing the original
            time series. The list is not assumed to be sorted.
        start: The start timestamp for the new resampled series (inclusive).
        end: The end timestamp for the new resampled series (inclusive).
        interval: The time step between consecutive points in the new series.

    Returns:
        A list of (timestamp, value) tuples for the resampled series.
        Timestamps range from `start` to `end` with a step of `interval`.
        Values are either a float from the original series or None.

    Raises:
        ValueError: If `interval` is not a positive integer.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")

    # Sort a copy of the points by timestamp to enable efficient processing.
    sorted_points = sorted(points)

    resampled = []
    points_idx = 0
    num_points = len(sorted_points)
    last_known_value: float | None = None

    for ts in range(start, end + 1, interval):
        # Advance through sorted_points to find the latest value at or before ts.
        while points_idx < num_points and sorted_points[points_idx][0] <= ts:
            last_known_value = sorted_points[points_idx][1]
            points_idx += 1

        resampled.append((ts, last_known_value))

    return resampled
