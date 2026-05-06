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
    """Return regularly spaced (timestamp, value) pairs from start to end inclusive.

    For each output timestamp, the value is forward-filled from the latest
    input point whose timestamp is <= the output timestamp.  When no such
    point exists, the value is None.

    If max_gap is specified, forward-filling is suppressed when the distance
    from the last observed input timestamp to the current output timestamp
    exceeds max_gap; None is emitted in that case.

    Args:
        points:   Unsorted list of (timestamp, value) pairs.
        start:    First output timestamp.
        end:      Last output timestamp (inclusive when reachable by interval).
        interval: Step between consecutive output timestamps; must be > 0.
        max_gap:  Optional maximum allowed distance (in timestamp units) between
                  the last observed point and the current output timestamp for
                  forward-fill to apply.  None means no limit.

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
    last_observed_ts: int | None = None

    ts = start
    while ts <= end:
        # Advance the pointer to consume all input points with timestamp <= ts.
        while point_index < n and sorted_points[point_index][0] <= ts:
            current_value = sorted_points[point_index][1]
            last_observed_ts = sorted_points[point_index][0]
            point_index += 1

        if current_value is None:
            value: float | None = None
        elif max_gap is not None and last_observed_ts is not None and (ts - last_observed_ts) > max_gap:
            value = None
        else:
            value = current_value

        output.append((ts, value))
        ts += interval

    return output
