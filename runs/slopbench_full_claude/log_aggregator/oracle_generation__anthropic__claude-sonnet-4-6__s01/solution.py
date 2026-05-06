"""
log_aggregator.py

Merge multiple log streams, deduplicate by (source, seq), sort by ts.
"""

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge log records from multiple streams.

    Deduplicates records by the composite key (source, seq).
    Returns a new list of records sorted ascending by 'ts'.
    Input records are not mutated.

    Parameters
    ----------
    streams:
        A list of iterables, each yielding log record dicts.
        Each record is expected to have at least 'source', 'seq', and 'ts' keys.

    Returns
    -------
    list[dict]
        Deduplicated records sorted by 'ts'.
    """
    if not isinstance(streams, list):
        raise TypeError(f"streams must be a list, got {type(streams).__name__}")

    seen: dict[tuple, dict] = {}

    for stream in streams:
        for record in stream:
            _validate_record(record)
            key = (record["source"], record["seq"])
            if key not in seen:
                seen[key] = dict(record)  # shallow copy; do not mutate original

    return sorted(seen.values(), key=lambda r: r["ts"])


def _validate_record(record: dict) -> None:
    """Raise ValueError if the record is missing required keys."""
    if not isinstance(record, dict):
        raise TypeError(f"Each log record must be a dict, got {type(record).__name__}")
    for field in ("source", "seq", "ts"):
        if field not in record:
            raise ValueError(f"Log record missing required field '{field}': {record!r}")
