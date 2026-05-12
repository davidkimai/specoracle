"""
time_series_resampler.py

Implements resample_series for resampling irregular time-series data onto a
regular grid using forward-fill semantics.
"""

from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Resample irregular time-series data onto a regular grid.

    Parameters
    ----------
    points:
        Input data as a list of (timestamp, value) tuples.  The list need not
        be sorted.
    start:
        First timestamp of the output grid (inclusive).
    end:
        Last timestamp of the output grid (inclusive).
    interval:
        Step between consecutive output timestamps.

    Returns
    -------
    list[tuple[int, float | None]]
        One entry per grid timestamp.  Each value is the most-recent known
        value at or before that timestamp (forward-fill), or ``None`` when no
        input point exists at or before the timestamp.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    # Sort input points by timestamp so we can sweep through them efficiently.
    sorted_points: list[tuple[int, float]] = sorted(points, key=lambda p: p[0])

    result: list[tuple[int, float | None]] = []

    # Index into sorted_points; we advance it as the output timestamp grows.
    ptr = 0
    n = len(sorted_points)
    last_value: float | None = None

    ts = start
    while ts <= end:
        # Advance the pointer past all points whose timestamp <= ts.
        while ptr < n and sorted_points[ptr][0] <= ts:
            last_value = sorted_points[ptr][1]
            ptr += 1

        result.append((ts, last_value))
        ts += interval

    return result
