from collections.abc import Iterable
from typing import Any


def merge_logs(streams: list[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Merge log streams, deduplicate by (source, seq), and sort by ts."""
    seen = set()
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
