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

    Deduplication key: (source, seq).
    Sort key: ts.

    Args:
        streams: A list of iterables, each yielding log record dicts.
        detect_gaps: When True, also return a list of gap dicts describing
                     missing sequence numbers between observed records per source.

    Returns:
        When detect_gaps is False (default):
            A deduplicated, ts-sorted list of log record dicts (copies).
        When detect_gaps is True:
            A tuple (merged_records, gaps) where gaps is a list of dicts
            {'source': <source>, 'missing_seq': <seq>} for every integer
            sequence number absent between the min and max observed seq
            values per source.  Only sources whose seq values are all
            integers are checked for gaps.

    Raises:
        TypeError: If streams is not a list, or any record is not a dict.
        KeyError: If a record is missing 'source' or 'seq'.
    """
    if not isinstance(streams, list):
        raise TypeError(f"streams must be a list, got {type(streams).__name__}")

    seen: dict[tuple, dict] = {}
    # Map source -> set of observed seq values (kept separately to avoid
    # coupling dedup logic with gap detection)
    source_seqs: dict = {}

    for stream in streams:
        for record in stream:
            if not isinstance(record, dict):
                raise TypeError(
                    f"Each log record must be a dict, got {type(record).__name__}"
                )
            if "source" not in record:
                raise KeyError(
                    f"Log record missing required key 'source': {record!r}"
                )
            if "seq" not in record:
                raise KeyError(
                    f"Log record missing required key 'seq': {record!r}"
                )

            key = (record["source"], record["seq"])
            if key not in seen:
                seen[key] = dict(record)

            if detect_gaps:
                src = record["source"]
                if src not in source_seqs:
                    source_seqs[src] = set()
                source_seqs[src].add(record["seq"])

    merged = sorted(seen.values(), key=_ts_sort_key)

    if not detect_gaps:
        return merged

    gaps: list[dict] = []
    for src, seqs in source_seqs.items():
        # Only perform gap detection when every seq value is an integer
        if not all(isinstance(s, int) for s in seqs):
            continue
        min_seq = min(seqs)
        max_seq = max(seqs)
        for missing in range(min_seq, max_seq + 1):
            if missing not in seqs:
                gaps.append({"source": src, "missing_seq": missing})

    # Sort gaps for deterministic output: by source then missing_seq
    gaps.sort(key=lambda g: (g["source"], g["missing_seq"]))

    return merged, gaps


def _ts_sort_key(record: dict):
    """Extract the ts value for sorting; records without ts sort last."""
    return (record.get("ts") is None, record.get("ts"))
