"""Utilities for merging log records."""


from collections.abc import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """Merge log streams, deduplicate by (source, seq), and sort by ts.

    Duplicate records keep the first occurrence encountered while iterating
    streams in order. Returned records are shallow copies of the inputs.
    """
    seen = set()
    merged = []

    for stream in streams:
        for record in stream:
            key = (record["source"], record["seq"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(dict(record))

    merged.sort(key=lambda record: record["ts"])
    return merged
