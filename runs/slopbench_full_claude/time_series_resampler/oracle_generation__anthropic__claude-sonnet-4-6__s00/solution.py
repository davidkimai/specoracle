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
    """Return regularly spaced (timestamp, value) pairs from start to end inclusive.

    For each output timestamp, the value is forward-filled from the latest
    input point whose timestamp is <= the output timestamp.  When no such
    point exists, the value is None.

    Args:
        points:   Unsorted list of (timestamp, value) pairs.
        start:    First output timestamp.
        end:      Last output timestamp (inclusive when reachable by interval).
        interval: Step between consecutive output timestamps; must be > 0.

    Raises:
        ValueError: If interval <= 0 or start > end.
    """
    if interval <= 0:
        raise ValueError(f"interval must be positive, got {interval!r}")
    if start > end:
        raise ValueError(f"start ({start}) must be <= end ({end})")

    sorted_points = sorted(points, key=lambda p: p[0])

    output: list[tuple[int, float | None]] = []
    point_index = 0
    n = len(sorted_points)
    current_value: float | None = None

    ts = start
    while ts <= end:
        # Advance the pointer to consume all input points with timestamp <= ts.
        while point_index < n and sorted_points[point_index][0] <= ts:
            current_value = sorted_points[point_index][1]
            point_index += 1

        output.append((ts, current_value))
        ts += interval

    return output
