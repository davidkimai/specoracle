from collections.abc import Iterable, Mapping
from typing import Any

__all__ = ["merge_logs"]

_REQUIRED_FIELDS = ("source", "seq", "ts")


def merge_logs(streams: list[Iterable[dict]]) -> list[dict]:
    """Merge log streams, deduplicate by (source, seq), and sort by timestamp.

    For duplicate (source, seq) keys, the first record encountered is retained.
    Returned records are shallow copies, so this function does not mutate input
    record dictionaries.
    """
    if not isinstance(streams, list):
        raise TypeError("streams must be a list of iterables")

    records_by_key: dict[tuple[Any, Any], dict] = {}

    for stream_index, stream in enumerate(streams):
        if not isinstance(stream, Iterable):
            raise TypeError(f"streams[{stream_index}] must be iterable")

        for record_index, record in enumerate(stream):
            copied_record = _copy_valid_record(record, stream_index, record_index)
            key = _deduplication_key(copied_record, stream_index, record_index)

            if key not in records_by_key:
                records_by_key[key] = copied_record

    return _sort_by_timestamp(records_by_key.values())


def _copy_valid_record(record: object, stream_index: int, record_index: int) -> dict:
    if not isinstance(record, Mapping):
        location = _record_location(stream_index, record_index)
        raise TypeError(f"{location} must be a dict-like mapping")

    missing_fields = [field for field in _REQUIRED_FIELDS if field not in record]
    if missing_fields:
        location = _record_location(stream_index, record_index)
        fields = ", ".join(repr(field) for field in missing_fields)
        raise ValueError(f"{location} is missing required field(s): {fields}")

    return dict(record)


def _deduplication_key(
    record: Mapping[str, Any],
    stream_index: int,
    record_index: int,
) -> tuple[Any, Any]:
    key = (record["source"], record["seq"])

    try:
        hash(key)
    except TypeError as exc:
        location = _record_location(stream_index, record_index)
        raise TypeError(f"{location} has unhashable source or seq") from exc

    return key


def _sort_by_timestamp(records: Iterable[dict]) -> list[dict]:
    try:
        return sorted(records, key=lambda record: record["ts"])
    except TypeError as exc:
        raise TypeError("log record timestamps must be mutually comparable") from exc


def _record_location(stream_index: int, record_index: int) -> str:
    return f"log record at streams[{stream_index}][{record_index}]"
