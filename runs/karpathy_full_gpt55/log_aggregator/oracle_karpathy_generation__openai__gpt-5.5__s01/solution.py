from collections.abc import Iterable


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """Merge log streams, deduplicate by (source, seq), and sort by ts.

    If duplicate records have the same (source, seq), the first record encountered
    is kept. Returned records are shallow copies of input records.
    """
    seen = set()
    records = []

    for stream in streams:
        for record in stream:
            key = (record["source"], record["seq"])
            if key in seen:
                continue
            seen.add(key)
            records.append(record.copy())

    records.sort(key=lambda record: record["ts"])
    return records
