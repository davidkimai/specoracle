"""
log_aggregator.py

Merges multiple log streams, deduplicates records by (source, seq),
and returns records sorted by timestamp (ts).
"""

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge multiple log streams into a single deduplicated, sorted list.

    Parameters
    ----------
    streams : list[Iterable[dict]]
        A list of iterables, each yielding log record dicts.
        Each record is expected to have at least the keys:
            - 'ts'     : comparable timestamp value used for sorting
            - 'source' : identifies the origin of the log record
            - 'seq'    : sequence number within that source

    Returns
    -------
    list[dict]
        Deduplicated records (by (source, seq)) sorted ascending by 'ts'.
        Input records are not mutated; shallow copies are stored.
    """
    seen: set[tuple] = set()
    merged: list[dict] = []

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key not in seen:
                seen.add(key)
                # Shallow copy to avoid mutating the original
                merged.append(dict(record))

    merged.sort(key=lambda r: r.get("ts"))
    return merged
