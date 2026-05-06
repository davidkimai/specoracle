"""
log_aggregator.py

Merges multiple log streams, deduplicates records by (source, seq),
and returns records sorted by timestamp (ts).
"""

from __future__ import annotations

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge multiple log streams into a single sorted, deduplicated list.

    Parameters
    ----------
    streams : list[Iterable[dict]]
        A list of iterables, each yielding log record dicts.
        Each record is expected to contain at least:
            - "ts"     : a comparable timestamp value
            - "source" : a hashable identifier for the log source
            - "seq"    : a sequence number (or any hashable dedup key)

    Returns
    -------
    list[dict]
        Copies of the deduplicated records, sorted ascending by "ts".
        Input records are never mutated.
    """
    seen: set[tuple] = set()
    merged: list[dict] = []

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key not in seen:
                seen.add(key)
                # Shallow copy to avoid mutating the original record
                merged.append(dict(record))

    merged.sort(key=lambda r: r.get("ts"))
    return merged
