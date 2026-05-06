"""
time_series_resampler.py

Resample a time series of (timestamp, value) points onto a regular grid.
"""

from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
) -> list[tuple[int, float | None]]:
    """Return timestamps from *start* to *end* (inclusive) spaced by *interval*.

    Each output value is the forward-fill of the latest input point whose
    timestamp is <= the output timestamp.  If no such point exists the value
    is ``None``.

    Parameters
    ----------
    points:
        Unsorted or sorted sequence of ``(timestamp, value)`` pairs.
    start:
        First timestamp of the output grid.
    end:
        Last timestamp of the output grid (included when reachable by the grid).
    interval:
        Step between consecutive output timestamps.  Must be > 0.

    Returns
    -------
    list[tuple[int, float | None]]
        Regularly-spaced ``(timestamp, value | None)`` pairs.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    # Sort input points by timestamp so we can do a linear scan.
    sorted_points: list[tuple[int, float]] = sorted(points, key=lambda p: p[0])

    result: list[tuple[int, float | None]] = []

    # Pointer into sorted_points; advances as we move through output timestamps.
    ptr = 0
    n = len(sorted_points)
    current_value: float | None = None

    ts = start
    while ts <= end:
        # Advance pointer while the next point's timestamp is <= ts.
        while ptr < n and sorted_points[ptr][0] <= ts:
            current_value = sorted_points[ptr][1]
            ptr += 1

        result.append((ts, current_value))
        ts += interval

    return result
