from __future__ import annotations


def resample_series(
    points: list[tuple[int, float]],
    *,
    start: int,
    end: int,
    interval: int,
    max_gap: int | None = None,
) -> list[tuple[int, float | None]]:
    ordered = sorted(points)
    index = 0
    current = None
    last_observed_ts: int | None = None
    output = []
    for timestamp in range(start, end + 1, interval):
        while index < len(ordered) and ordered[index][0] <= timestamp:
            last_observed_ts = ordered[index][0]
            current = ordered[index][1]
            index += 1
        if current is None:
            value: float | None = None
        elif max_gap is not None and last_observed_ts is not None and (timestamp - last_observed_ts) > max_gap:
            value = None
        else:
            value = current
        output.append((timestamp, value))
    return output
