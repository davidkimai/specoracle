"""
log_aggregator.py

Merge multiple log streams, deduplicate by (source, seq), sort by ts.
"""

from __future__ import annotations

from typing import Iterable


def merge_logs(
    streams: list[Iterable[dict]],
    detect_gaps: bool = False,
) -> list[dict] | tuple[list[dict], list[dict]]:
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
    detect_gaps:
        When True, also return a list of gap dicts.  Each gap dict has
        the keys 'source' and 'missing_seq', one entry per missing
        sequence number between the minimum and maximum observed seq
        value for that source.

    Returns
    -------
    list[dict]
        Deduplicated, ts-sorted list of shallow-copied log records.
        (when detect_gaps is False)

    tuple[list[dict], list[dict]]
        (merged_records, gaps) when detect_gaps is True.
        gaps contains {'source': ..., 'missing_seq': ...} for every
        integer sequence number that lies between the min and max
        observed seq for a source but was never seen.
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

    if not detect_gaps:
        return merged

    # Build per-source set of observed seq values.
    source_seqs: dict[str, set] = {}
    for record in merged:
        source = record["source"]
        seq = record["seq"]
        if source not in source_seqs:
            source_seqs[source] = set()
        source_seqs[source].add(seq)

    gaps: list[dict] = []
    for source, seqs in source_seqs.items():
        min_seq = min(seqs)
        max_seq = max(seqs)
        # Only attempt integer range detection when seq values are integers.
        try:
            min_seq_int = int(min_seq)
            max_seq_int = int(max_seq)
        except (TypeError, ValueError):
            continue
        for candidate in range(min_seq_int, max_seq_int + 1):
            if candidate not in seqs:
                gaps.append({"source": source, "missing_seq": candidate})

    return merged, gaps


def _validate_record_keys(record: dict, stream_index: int) -> None:
    """Raise ValueError if a required key is absent from a log record."""
    required = ("source", "seq", "ts")
    missing = [k for k in required if k not in record]
    if missing:
        raise ValueError(
            f"Log record in stream {stream_index} is missing required "
            f"key(s): {missing!r}.  Record: {record!r}"
        )
