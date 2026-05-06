"""
log_aggregator.py

Merge multiple log streams, deduplicate by (source, seq), sort by ts.
"""

from typing import Iterable


def merge_logs(
    streams: list[Iterable[dict]],
    detect_gaps: bool = False,
) -> "list[dict] | tuple[list[dict], list[dict]]":
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
    detect_gaps:
        When True, also return a list of gap dicts {'source', 'missing_seq'}
        for every integer sequence number missing between the minimum and
        maximum observed seq per source.  The return value becomes a tuple
        (merged_records, gaps).

    Returns
    -------
    list[dict]
        Deduplicated records sorted by 'ts'  (when detect_gaps is False).
    tuple[list[dict], list[dict]]
        (merged_records, gaps)  (when detect_gaps is True).
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

    merged = sorted(seen.values(), key=lambda r: r["ts"])

    if not detect_gaps:
        return merged

    # Build per-source set of observed seq values.
    source_seqs: dict[str, set] = {}
    for key, record in seen.items():
        source = key[0]
        seq = key[1]
        source_seqs.setdefault(source, set()).add(seq)

    gaps: list[dict] = []
    for source, seqs in sorted(source_seqs.items()):
        try:
            min_seq = min(seqs)
            max_seq = max(seqs)
        except (TypeError, ValueError):
            # seq values are not comparable as integers; skip gap detection
            continue
        try:
            full_range = range(int(min_seq), int(max_seq) + 1)
        except (TypeError, ValueError):
            continue
        for missing in full_range:
            if missing not in seqs:
                gaps.append({"source": source, "missing_seq": missing})

    return merged, gaps


def _validate_record(record: dict) -> None:
    """Raise ValueError if the record is missing required keys."""
    if not isinstance(record, dict):
        raise TypeError(f"Each log record must be a dict, got {type(record).__name__}")
    for field in ("source", "seq", "ts"):
        if field not in record:
            raise ValueError(f"Log record missing required field '{field}': {record!r}")
