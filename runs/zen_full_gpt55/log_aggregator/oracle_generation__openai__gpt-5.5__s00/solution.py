from collections.abc import Hashable, Iterable
from typing import Any


_REQUIRED_KEYS = ("source", "seq", "ts")


def merge_logs(streams: list[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Merge log streams, deduplicate by (source, seq), and sort by timestamp."""
    if not isinstance(streams, list):
        raise TypeError("streams must be a list of iterables")

    records_by_key: dict[tuple[Hashable, Hashable], dict[str, Any]] = {}

    for stream_index, stream in enumerate(streams):
        _require_iterable(stream, stream_index)

        for record_index, record in enumerate(stream):
            key = _record_key(record, stream_index, record_index)

            if key in records_by_key:
                continue

            records_by_key[key] = dict(record)

    return _sort_by_timestamp(list(records_by_key.values()))


def _require_iterable(stream: Iterable[dict[str, Any]], stream_index: int) -> None:
    if isinstance(stream, (str, bytes)):
        raise TypeError(f"stream at index {stream_index} must be an iterable of dict records")

    try:
        iter(stream)
    except TypeError as exc:
        raise TypeError(f"stream at index {stream_index} must be iterable") from exc


def _record_key(
    record: dict[str, Any],
    stream_index: int,
    record_index: int,
) -> tuple[Hashable, Hashable]:
    if not isinstance(record, dict):
        raise TypeError(
            f"record at stream {stream_index}, index {record_index} must be a dict"
        )

    for key in _REQUIRED_KEYS:
        if key not in record:
            raise KeyError(
                f"record at stream {stream_index}, index {record_index} is missing {key!r}"
            )

    source = record["source"]
    seq = record["seq"]

    if not isinstance(source, Hashable):
        raise TypeError(
            f"record at stream {stream_index}, index {record_index} has unhashable source"
        )

    if not isinstance(seq, Hashable):
        raise TypeError(
            f"record at stream {stream_index}, index {record_index} has unhashable seq"
        )

    return source, seq


def _sort_by_timestamp(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        return sorted(records, key=lambda record: record["ts"])
    except TypeError as exc:
        raise TypeError("record timestamps must be mutually comparable") from exc
