"""
log_aggregator.py

Merge multiple log streams, deduplicate by (source, seq), sort by ts.
"""

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge log records from multiple streams.

    Deduplication key: (source, seq).
    Sort key: ts.

    Args:
        streams: A list of iterables, each yielding log record dicts.

    Returns:
        A deduplicated, ts-sorted list of log record dicts (copies).

    Raises:
        TypeError: If streams is not a list, or any record is not a dict.
        KeyError: If a record is missing 'source' or 'seq'.
    """
    if not isinstance(streams, list):
        raise TypeError(f"streams must be a list, got {type(streams).__name__}")

    seen: dict[tuple, dict] = {}

    for stream in streams:
        for record in stream:
            if not isinstance(record, dict):
                raise TypeError(f"Each log record must be a dict, got {type(record).__name__}")
            if "source" not in record:
                raise KeyError(f"Log record missing required key 'source': {record!r}")
            if "seq" not in record:
                raise KeyError(f"Log record missing required key 'seq': {record!r}")

            key = (record["source"], record["seq"])
            if key not in seen:
                seen[key] = dict(record)

    return sorted(seen.values(), key=_ts_sort_key)


def _ts_sort_key(record: dict):
    """Extract the ts value for sorting; records without ts sort last."""
    return (record.get("ts") is None, record.get("ts"))
