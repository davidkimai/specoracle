"""
log_aggregator.py

Provides merge_logs for merging, deduplicating, and sorting log records
from multiple streams.
"""

from __future__ import annotations

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """Merge multiple log streams into a single sorted, deduplicated list.

    Records are deduplicated by the composite key (source, seq).  When
    duplicate keys are encountered the first record seen is kept (stream
    order, then insertion order within each stream).  The returned list is
    sorted ascending by the 'ts' field.  Input records are never mutated;
    shallow copies are stored internally.

    Parameters
    ----------
    streams:
        A list of iterables, each yielding log record dicts.  Each record
        is expected to contain at least the keys 'source', 'seq', and 'ts'.

    Returns
    -------
    list[dict]
        Merged, deduplicated records sorted by 'ts'.
    """
    seen: dict[tuple, dict] = {}

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key not in seen:
                # Store a shallow copy so the originals are never mutated.
                seen[key] = dict(record)

    merged = list(seen.values())
    merged.sort(key=lambda r: r.get("ts"))
    return merged
