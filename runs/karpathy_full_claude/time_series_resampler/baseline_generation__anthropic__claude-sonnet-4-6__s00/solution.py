"""
time_series_resampler.py

Provides resample_series: resamples a time series to regular intervals using
forward-fill logic.
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
    Resample an irregular time series to regular timestamps.

    Parameters
    ----------
    points:
        A list of (timestamp, value) pairs.  Need not be sorted.
    start:
        First timestamp of the output grid (inclusive).
    end:
        Last timestamp of the output grid (inclusive).
    interval:
        Step between consecutive output timestamps.

    Returns
    -------
    list[tuple[int, float | None]]
        One entry per grid timestamp.  Each value is the last known value at or
        before the timestamp (forward-fill), or None if no such point exists.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    # Sort input points by timestamp so we can scan them in order.
    sorted_points: list[tuple[int, float]] = sorted(points, key=lambda p: p[0])

    result: list[tuple[int, float | None]] = []

    # Pointer into sorted_points; we advance it as the grid timestamp grows.
    ptr = 0
    n = len(sorted_points)
    last_value: float | None = None

    ts = start
    while ts <= end:
        # Consume all input points whose timestamp <= ts.
        while ptr < n and sorted_points[ptr][0] <= ts:
            last_value = sorted_points[ptr][1]
            ptr += 1

        result.append((ts, last_value))
        ts += interval

    return result
