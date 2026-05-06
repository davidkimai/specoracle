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
        Each iterable yields log record dicts. Records are expected to
        contain at least the keys 'source', 'seq', and 'ts'.
    detect_gaps : bool, optional
        When True, also return a list of gap dicts describing missing
        sequence numbers between the min and max observed seq per source.
        Each gap dict has the keys 'source' and 'missing_seq'.

    Returns
    -------
    list[dict]
        Deduplicated records sorted ascending by 'ts' (when detect_gaps
        is False).
    tuple[list[dict], list[dict]]
        (merged_records, gaps) when detect_gaps is True. gaps contains
        one dict per missing sequence number:
        {'source': <source>, 'missing_seq': <seq>}.

    Notes
    -----
    Input records are not mutated; shallow copies are returned.
    """
    seen: set[tuple] = set()
    merged: list[dict] = []
    # Maps source -> set of observed seq values (only tracked when needed)
    source_seqs: dict = {}

    for stream in streams:
        for record in stream:
            key = (record.get("source"), record.get("seq"))
            if key not in seen:
                seen.add(key)
                # Return a shallow copy so we never mutate the original.
                merged.append(dict(record))

            if detect_gaps:
                source = record.get("source")
                seq = record.get("seq")
                if source is not None and seq is not None:
                    if source not in source_seqs:
                        source_seqs[source] = set()
                    source_seqs[source].add(seq)

    merged.sort(key=lambda r: r.get("ts"))

    if not detect_gaps:
        return merged

    gaps: list[dict] = []
    for source, seqs in source_seqs.items():
        try:
            min_seq = min(seqs)
            max_seq = max(seqs)
        except (TypeError, ValueError):
            # Non-comparable seq values; skip gap detection for this source.
            continue
        try:
            full_range = range(min_seq, max_seq + 1)
        except TypeError:
            # seq values are not integers; skip gap detection for this source.
            continue
        for missing in full_range:
            if missing not in seqs:
                gaps.append({"source": source, "missing_seq": missing})

    return merged, gaps
