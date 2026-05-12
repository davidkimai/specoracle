from collections.abc import Iterable
from typing import Any


def merge_logs(streams: list[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    """
    Merge log streams, deduplicate by (source, seq), and return records sorted by ts.

    When duplicate records with the same (source, seq) are encountered, the first
    one seen in stream order is retained. Returned records are shallow copies of
    the input dictionaries.
    """
    seen: set[tuple[Any, Any]] = set()
    merged: list[dict[str, Any]] = []

    for stream in streams:
        for record in stream:
            dedupe_key = (record["source"], record["seq"])
            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)
            merged.append(dict(record))

    merged.sort(key=lambda record: record["ts"])
    return merged
