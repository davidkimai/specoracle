"""
log_aggregator.py

Merge multiple log streams, deduplicate by (source, seq), sort by ts.
"""

from __future__ import annotations

from typing import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge log records from multiple streams.

    Each record is expected to be a dict with at least the keys:
        - 'source': identifies the origin of the log record
        - 'seq':    sequence number within that source
        - 'ts':     timestamp used for final ordering

    Records are deduplicated by the (source, seq) pair; the first
    occurrence wins.  The returned list is sorted ascending by 'ts'.
    Input records are never mutated; shallow copies are returned.

    Parameters
    ----------
    streams:
        A list of iterables, each yielding log-record dicts.

    Returns
    -------
    list[dict]
        Deduplicated, ts-sorted list of shallow-copied log records.
    """
    if not isinstance(streams, list):
        raise TypeError(f"streams must be a list, got {type(streams).__name__!r}")

    seen: set[tuple] = set()
    merged: list[dict] = []

    for stream_index, stream in enumerate(streams):
        for record in stream:
            if not isinstance(record, dict):
                raise TypeError(
                    f"Each log record must be a dict, got "
                    f"{type(record).__name__!r} in stream {stream_index}"
                )
            _validate_record_keys(record, stream_index)

            key = (record["source"], record["seq"])
            if key in seen:
                continue

            seen.add(key)
            merged.append(dict(record))  # shallow copy; no mutation of input

    merged.sort(key=lambda r: r["ts"])
    return merged


def _validate_record_keys(record: dict, stream_index: int) -> None:
    """Raise ValueError if a required key is absent from a log record."""
    required = ("source", "seq", "ts")
    missing = [k for k in required if k not in record]
    if missing:
        raise ValueError(
            f"Log record in stream {stream_index} is missing required "
            f"key(s): {missing!r}.  Record: {record!r}"
        )
