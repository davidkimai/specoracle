"""
time_series_resampler.py

Provides resample_series() for resampling irregular time-series data onto a
regular grid using forward-fill semantics.
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
    """Resample *points* onto a regular grid.

    Parameters
    ----------
    points:
        Unsorted or sorted sequence of (timestamp, value) pairs.
    start:
        First timestamp of the output grid (inclusive).
    end:
        Last timestamp of the output grid (inclusive).
    interval:
        Step between consecutive output timestamps.
    max_gap:
        Optional maximum distance (in timestamp units) between the last
        observed point and a grid timestamp.  When the gap exceeds this
        value, ``None`` is emitted instead of forward-filling.  When
        ``None`` (default), forward-fill is unbounded.

    Returns
    -------
    list[tuple[int, float | None]]
        One entry per grid timestamp.  Each value is the latest known reading
        whose timestamp is <= the grid timestamp, or ``None`` if no such
        reading exists yet (or if the gap to the last known reading exceeds
        *max_gap*).
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    # Sort input points by timestamp so we can do a linear scan.
    sorted_points: list[tuple[int, float]] = sorted(points, key=lambda p: p[0])

    result: list[tuple[int, float | None]] = []
    src_idx = 0
    src_len = len(sorted_points)
    last_value: float | None = None
    last_ts: int | None = None

    ts = start
    while ts <= end:
        # Advance through sorted_points as long as the next point's timestamp
        # is still <= ts (forward-fill: we keep the *latest* value <= ts).
        while src_idx < src_len and sorted_points[src_idx][0] <= ts:
            last_ts = sorted_points[src_idx][0]
            last_value = sorted_points[src_idx][1]
            src_idx += 1

        if last_value is None:
            result.append((ts, None))
        elif max_gap is not None and last_ts is not None and (ts - last_ts) > max_gap:
            result.append((ts, None))
        else:
            result.append((ts, last_value))

        ts += interval

    return result
