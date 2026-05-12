"""Log aggregation utilities."""

from collections.abc import Iterable
from typing import Any


def merge_logs(streams: list[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Merge log streams, deduplicate by (source, seq), and sort by timestamp.

    The first record encountered for each (source, seq) pair is retained.
    Returned records are shallow copies so input record dictionaries are not
    mutated or exposed through the returned list.

    Args:
        streams: A list of iterables yielding log record dictionaries. Each
            record is expected to contain "source", "seq", and "ts" keys.

    Returns:
        A list of deduplicated log records sorted by their "ts" value.
    """
    seen: set[tuple[Any, Any]] = set()
    merged: list[dict[str, Any]] = []

    for stream in streams:
        for record in stream:
            key = (record["source"], record["seq"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(dict(record))

    merged.sort(key=lambda record: record["ts"])
    return merged
