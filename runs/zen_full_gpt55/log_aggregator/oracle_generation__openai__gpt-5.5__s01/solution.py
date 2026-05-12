from collections.abc import Iterable, Iterator
from typing import Any

__all__ = ["merge_logs"]

_REQUIRED_FIELDS = ("source", "seq", "ts")


def merge_logs(streams: list[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Merge log streams, keeping the first record seen for each (source, seq)."""
    _validate_streams_container(streams)

    records_by_key: dict[tuple[Any, Any], dict[str, Any]] = {}

    for stream_index, stream in enumerate(streams):
        for record_index, record in enumerate(_iter_stream(stream, stream_index)):
            copied_record = _validated_record_copy(record, stream_index, record_index)
            key = _record_key(copied_record, stream_index, record_index)
            if key not in records_by_key:
                records_by_key[key] = copied_record

    return _records_sorted_by_timestamp(list(records_by_key.values()))


def _validate_streams_container(streams: object) -> None:
    if not isinstance(streams, list):
        raise TypeError(
            f"streams must be a list of iterables, got {type(streams).__name__}"
        )


def _iter_stream(stream: object, stream_index: int) -> Iterator[Any]:
    try:
        return iter(stream)
    except TypeError as exc:
        raise TypeError(
            f"stream {stream_index} must be iterable, got {type(stream).__name__}"
        ) from exc


def _validated_record_copy(
    record: object,
    stream_index: int,
    record_index: int,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError(
            f"record {record_index} in stream {stream_index} must be a dict, "
            f"got {type(record).__name__}"
        )

    copied_record = dict(record)
    _require_fields(copied_record, stream_index, record_index)
    return copied_record


def _require_fields(
    record: dict[str, Any],
    stream_index: int,
    record_index: int,
) -> None:
    missing_fields = [field for field in _REQUIRED_FIELDS if field not in record]
    if missing_fields:
        fields = ", ".join(missing_fields)
        raise KeyError(
            f"record {record_index} in stream {stream_index} is missing "
            f"required field(s): {fields}"
        )


def _record_key(
    record: dict[str, Any],
    stream_index: int,
    record_index: int,
) -> tuple[Any, Any]:
    source = record["source"]
    seq = record["seq"]

    _require_hashable(source, "source", stream_index, record_index)
    _require_hashable(seq, "seq", stream_index, record_index)

    return source, seq


def _require_hashable(
    value: Any,
    field_name: str,
    stream_index: int,
    record_index: int,
) -> None:
    try:
        hash(value)
    except TypeError as exc:
        raise TypeError(
            f"record {record_index} in stream {stream_index} has unhashable "
            f"{field_name!r} value"
        ) from exc


def _records_sorted_by_timestamp(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        return sorted(records, key=_timestamp)
    except TypeError as exc:
        raise TypeError("log record 'ts' values must be mutually comparable") from exc


def _timestamp(record: dict[str, Any]) -> Any:
    return record["ts"]
