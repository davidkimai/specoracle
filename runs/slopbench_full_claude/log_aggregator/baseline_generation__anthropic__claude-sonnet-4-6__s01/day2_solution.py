"""
log_aggregator.py

Merges multiple log streams, deduplicates records by (source, seq),
and returns records sorted by timestamp (ts).

Day 2: Added detect_gaps parameter to identify missing sequence numbers
per source between the minimum and maximum observed seq values.
"""

from __future__ import annotations

from typing import Iterable


def merge_logs(
    streams: list[Iterable[dict]],
    detect_gaps: bool = False,
) -> list[dict] | tuple[list[dict], list[dict]]:
    """
    Merge multiple log streams into a single sorted, deduplicated list.

    Parameters
    ----------
    streams : list[Iterable[dict]]
        A list of iterables, each yielding log record dicts.
        Each record is expected to contain at least:
            - "ts"     : a comparable timestamp value
            - "source" : a hashable identifier for the log source
            - "seq"    : an integer sequence number (or any int-castable dedup key)

    detect_gaps : bool, optional
        When False (default), return the merged list as before.
        When True, return a tuple (merged_records, gaps) where gaps is a list
        of dicts, each with:
            - "source"      : the log source identifier
            - "missing_seq" : the missing sequence number

    Returns
    -------
    list[dict]
        When detect_gaps is False: copies of the deduplicated records,
        sorted ascending by "ts".
    tuple[list[dict], list[dict]]
        When detect_gaps is True: (merged_records, gaps).
    """
    seen: set[tuple] = set()
    merged: list[dict] = []
    # Maps source -> set of observed seq values (only when detect_gaps is True)
    source_seqs: dict = {} if detect_gaps else None  # type: ignore[assignment]

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key not in seen:
                seen.add(key)
                # Shallow copy to avoid mutating the original record
                merged.append(dict(record))

            if detect_gaps:
                source = record.get("source")
                seq = record.get("seq")
                if source is not None and seq is not None:
                    if source not in source_seqs:
                        source_seqs[source] = set()
                    try:
                        source_seqs[source].add(int(seq))
                    except (TypeError, ValueError):
                        pass

    merged.sort(key=lambda r: r.get("ts"))

    if not detect_gaps:
        return merged

    gaps: list[dict] = []
    for source, seqs in source_seqs.items():
        if len(seqs) < 2:
            continue
        min_seq = min(seqs)
        max_seq = max(seqs)
        for candidate in range(min_seq, max_seq + 1):
            if candidate not in seqs:
                gaps.append({"source": source, "missing_seq": candidate})

    return merged, gaps
