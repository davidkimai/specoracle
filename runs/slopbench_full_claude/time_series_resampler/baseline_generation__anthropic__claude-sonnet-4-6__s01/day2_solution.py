"""
time_series_resampler.py

Provides resample_series for resampling a time series to a regular grid.
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
    """Resample an irregular time series onto a regular grid.

    Parameters
    ----------
    points:
        List of (timestamp, value) pairs.  Need not be sorted.
    start:
        First timestamp of the output grid (inclusive).
    end:
        Last timestamp of the output grid (inclusive).
    interval:
        Step between consecutive output timestamps.
    max_gap:
        Optional maximum allowed distance between the last observed point and
        the current grid timestamp.  If the gap exceeds this value, None is
        emitted instead of forward-filling.  When None (default), forward-fill
        is always applied regardless of gap size.

    Returns
    -------
    list[tuple[int, float | None]]
        One entry per grid timestamp.  Each value is the forward-fill of the
        latest input point whose timestamp is <= the grid timestamp, or None
        when no such point exists (or when max_gap is set and the gap exceeds
        it).
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    if max_gap is not None and max_gap < 0:
        raise ValueError("max_gap must be a non-negative integer or None")

    # Sort input points by timestamp so we can binary-search efficiently.
    sorted_points: list[tuple[int, float]] = sorted(points, key=lambda p: p[0])

    # Extract just the timestamps for binary search.
    timestamps: list[int] = [p[0] for p in sorted_points]

    result: list[tuple[int, float | None]] = []

    ts = start
    while ts <= end:
        # Find the rightmost point with timestamp <= ts.
        # bisect_right gives the insertion position for ts+1 equivalent,
        # i.e., the index *after* all entries <= ts.
        lo, hi = 0, len(timestamps)
        while lo < hi:
            mid = (lo + hi) // 2
            if timestamps[mid] <= ts:
                lo = mid + 1
            else:
                hi = mid

        idx = lo - 1  # index of the latest point with timestamp <= ts
        if idx < 0:
            value: float | None = None
        else:
            # Check max_gap constraint.
            if max_gap is not None and (ts - timestamps[idx]) > max_gap:
                value = None
            else:
                value = sorted_points[idx][1]

        result.append((ts, value))
        ts += interval

    return result
