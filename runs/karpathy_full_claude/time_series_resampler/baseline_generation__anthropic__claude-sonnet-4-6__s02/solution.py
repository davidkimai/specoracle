"""
time_series_resampler.py

Implements resample_series for resampling a time series with forward-fill logic.
"""

from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """
    Resample a time series onto a regular grid.

    Parameters
    ----------
    points   : list of (timestamp, value) pairs (need not be sorted)
    start    : first timestamp of the output grid (inclusive)
    end      : last  timestamp of the output grid (inclusive)
    interval : step between consecutive output timestamps

    Returns
    -------
    List of (timestamp, value | None) tuples.
    Each output timestamp carries the value of the latest input point whose
    timestamp is <= that output timestamp, or None if no such point exists.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    # Sort input points by timestamp so we can do a linear scan.
    sorted_points = sorted(points, key=lambda p: p[0])

    result: list[tuple[int, float | None]] = []
    ptr = 0          # index into sorted_points
    n = len(sorted_points)
    current_value: float | None = None

    ts = start
    while ts <= end:
        # Advance the pointer while the next point's timestamp <= ts
        while ptr < n and sorted_points[ptr][0] <= ts:
            current_value = sorted_points[ptr][1]
            ptr += 1

        result.append((ts, current_value))
        ts += interval

    return result
