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
) -> list[tuple[int, float | None]]:
    """Return a regularly-spaced series from start to end (inclusive) by interval.

    Each output timestamp carries the most recent known value at or before that
    timestamp (forward-fill).  If no input point exists at or before a timestamp
    the value is None.

    Args:
        points:   Unsorted or sorted sequence of (timestamp, value) pairs.
        start:    First output timestamp.
        end:      Last output timestamp (included when reachable by interval).
        interval: Step between consecutive output timestamps (must be > 0).

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

    ts = start
    while ts <= end:
        # Advance the source pointer while the next point is at or before ts.
        while source_index < source_len and sorted_points[source_index][0] <= ts:
            current_value = sorted_points[source_index][1]
            source_index += 1

        output.append((ts, current_value))
        ts += interval

    return output
