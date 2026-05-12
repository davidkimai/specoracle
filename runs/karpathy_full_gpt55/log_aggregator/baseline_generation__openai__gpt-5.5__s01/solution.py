"""Log aggregation utilities."""

from typing import Iterable, Any


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """
    Merge multiple log streams, deduplicate records by (source, seq), and return
    records sorted by timestamp.

    The first record encountered for a given (source, seq) pair is retained.
    Returned records are shallow copies so input records are not mutated or
    exposed directly.
    """
    seen: set[tuple[Any, Any]] = set()
    merged: list[dict] = []

    for stream in streams:
        for record in stream:
            key = (record["source"], record["seq"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(dict(record))

    merged.sort(key=lambda record: record["ts"])
    return merged


__all__ = ["merge_logs"]
