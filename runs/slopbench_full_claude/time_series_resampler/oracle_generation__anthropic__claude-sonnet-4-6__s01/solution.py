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

    Each output timestamp carries the most recent known value at or before that
    timestamp (forward-fill).  When no input point exists at or before a
    timestamp, the value is None.

    Parameters
    ----------
    points:
        Irregular (timestamp, value) pairs.  Need not be sorted.
    start:
        First output timestamp.
    end:
        Last output timestamp (inclusive when reachable by the interval).
    interval:
        Step between consecutive output timestamps.  Must be positive.
    """
    if interval <= 0:
        raise ValueError(f"interval must be positive, got {interval!r}")
    if start > end:
        raise ValueError(
            f"start ({start!r}) must be less than or equal to end ({end!r})"
        )

    sorted_points = sorted(points, key=lambda p: p[0])

    output: list[tuple[int, float | None]] = []
    point_index = 0
    n = len(sorted_points)
    last_value: float | None = None

    ts = start
    while ts <= end:
        # Advance the pointer past all input points whose timestamp <= ts.
        while point_index < n and sorted_points[point_index][0] <= ts:
            last_value = sorted_points[point_index][1]
            point_index += 1

        output.append((ts, last_value))
        ts += interval

    return output
