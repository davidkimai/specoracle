from __future__ import annotations

_TIMESTAMP_FIELD = "timestamp"
_MISSING = object()


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_events(events: object) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list")


def _validate_key_fields(key_fields: object) -> None:
    if not isinstance(key_fields, list):
        raise TypeError("key_fields must be a list of strings")

    for field in key_fields:
        if not isinstance(field, str):
            raise TypeError("key_fields must be a list of strings")


def _validate_window_seconds(window_seconds: object) -> None:
    if not _is_integer(window_seconds):
        raise TypeError("window_seconds must be a non-negative integer")

    if window_seconds < 0:
        raise ValueError("window_seconds must be a non-negative integer")


def _parse_event(event: object, key_fields: list[str]):
    if not isinstance(event, dict):
        return None

    timestamp = event.get(_TIMESTAMP_FIELD, _MISSING)
    if not _is_integer(timestamp):
        return None

    for field in key_fields:
        if field not in event:
            return None

    composite_key = tuple(event[field] for field in key_fields)
    return timestamp, composite_key


def _find_key_index(records: list[tuple[tuple[object, ...], int]], composite_key: tuple[object, ...]) -> int:
    for index, (record_key, _) in enumerate(records):
        if record_key == composite_key:
            return index

    return -1


def _is_duplicate(timestamp: int, kept_timestamp: int, window_seconds: int) -> bool:
    return timestamp < kept_timestamp + window_seconds


def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    _validate_events(events)
    _validate_key_fields(key_fields)
    _validate_window_seconds(window_seconds)

    retained = []
    kept_records = []

    for event in events:
        parsed_event = _parse_event(event, key_fields)
        if parsed_event is None:
            continue

        timestamp, composite_key = parsed_event
        key_index = _find_key_index(kept_records, composite_key)

        if key_index == -1:
            kept_records.append((composite_key, timestamp))
            retained.append(event)
            continue

        _, kept_timestamp = kept_records[key_index]
        if _is_duplicate(timestamp, kept_timestamp, window_seconds):
            continue

        kept_records[key_index] = (composite_key, timestamp)
        retained.append(event)

    return retained
