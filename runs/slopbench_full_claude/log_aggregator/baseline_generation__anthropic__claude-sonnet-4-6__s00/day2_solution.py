"""
log_aggregator.py

Provides merge_logs for merging, deduplicating, and sorting log records
from multiple streams.
"""

from typing import Iterable


def merge_logs(
    streams: list[Iterable[dict]],
    detect_gaps: bool = False,
) -> "list[dict] | tuple[list[dict], list[dict]]":
    """
    Merge multiple log streams, deduplicate records by (source, seq),
    and return records sorted by ts.

    Parameters
    ----------
    streams : list of iterables of dict
        Each iterable yields log record dicts that are expected to contain
        at least the keys 'source', 'seq', and 'ts'.
    detect_gaps : bool, optional
        When True, also return a list of gap records describing missing
        sequence numbers between the min and max observed seq per source.
        Default is False.

    Returns
    -------
    list of dict
        When detect_gaps is False (default): deduplicated records sorted
        by 'ts' in ascending order.
    tuple[list[dict], list[dict]]
        When detect_gaps is True: a 2-tuple of
        (merged_records, gaps), where gaps contains dicts with keys
        'source' and 'missing_seq' for each integer sequence number absent
        between the minimum and maximum observed seq for that source.
        Input records are not mutated; copies are returned.
    """
    seen: set[tuple] = set()
    merged: list[dict] = []
    # Maps source -> set of observed seq values (integers only)
    source_seqs: dict = {}

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key not in seen:
                seen.add(key)
                merged.append(dict(record))

            # Track seq numbers per source for gap detection
            if detect_gaps:
                source = record.get("source")
                seq = record.get("seq")
                if source is not None and isinstance(seq, int):
                    if source not in source_seqs:
                        source_seqs[source] = set()
                    source_seqs[source].add(seq)

    merged.sort(key=lambda r: r.get("ts"))

    if not detect_gaps:
        return merged

    gaps: list[dict] = []
    for source, seqs in source_seqs.items():
        min_seq = min(seqs)
        max_seq = max(seqs)
        for missing in range(min_seq, max_seq + 1):
            if missing not in seqs:
                gaps.append({"source": source, "missing_seq": missing})

    return merged, gaps
