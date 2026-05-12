"""
log_aggregator.py

Provides merge_logs for merging, deduplicating, and sorting log records
from multiple streams.
"""

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge multiple log streams, deduplicate records by (source, seq),
    and return records sorted by ts.

    Parameters
    ----------
    streams : list of iterables of dict
        Each iterable yields log record dicts.  Each record is expected to
        contain at least the keys ``source``, ``seq``, and ``ts``.

    Returns
    -------
    list of dict
        Deduplicated records (copies, originals are not mutated) sorted
        ascending by ``ts``.
    """
    seen: set[tuple] = set()
    merged: list[dict] = []

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key in seen:
                continue
            seen.add(key)
            # Shallow copy so we never mutate the caller's record.
            merged.append(dict(record))

    merged.sort(key=lambda r: r.get("ts"))
    return merged
