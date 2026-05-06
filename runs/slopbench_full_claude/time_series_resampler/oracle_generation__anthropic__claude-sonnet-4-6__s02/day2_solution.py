"""
time_series_resampler.py

Resample an irregular time series onto a regular grid using forward-fill.
"""

from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
    max_gap: int | None = None,
) -> list[tuple[int, float | None]]:
    """Return a regularly-spaced series from start to end (inclusive) by interval.

    Each output timestamp carries the most recent known value at or before that
    timestamp (forward-fill).  If no input point exists at or before a timestamp
    the value is None.

    If max_gap is given, forward-fill is suppressed when the distance from the
    last observed point to the current timestamp exceeds max_gap; None is emitted
    instead.

    Args:
        points:   Unsorted or sorted sequence of (timestamp, value) pairs.
        start:    First output timestamp.
        end:      Last output timestamp (included when reachable by interval).
        interval: Step between consecutive output timestamps (must be > 0).
        max_gap:  Optional maximum distance (inclusive) from the last known point
                  beyond which forward-fill is replaced with None.

    Returns:
        List of (timestamp, value | None) tuples.

    Raises:
        ValueError: If interval is not positive, or start > end.
    """
    if interval <= 0:
        raise ValueError(f"interval must be positive, got {interval!r}")
    if start > end:
        raise ValueError(f"start ({start}) must be <= end ({end})")

    sorted_points = sorted(points, key=lambda p: p[0])

    output: list[tuple[int, float | None]] = []
    source_index = 0
    source_len = len(sorted_points)
    current_value: float | None = None
    last_point_ts: int | None = None

    ts = start
    while ts <= end:
        # Advance the source pointer while the next point is at or before ts.
        while source_index < source_len and sorted_points[source_index][0] <= ts:
            last_point_ts = sorted_points[source_index][0]
            current_value = sorted_points[source_index][1]
            source_index += 1

        if current_value is None:
            output.append((ts, None))
        elif max_gap is not None and last_point_ts is not None and (ts - last_point_ts) > max_gap:
            output.append((ts, None))
        else:
            output.append((ts, current_value))

        ts += interval

    return output
