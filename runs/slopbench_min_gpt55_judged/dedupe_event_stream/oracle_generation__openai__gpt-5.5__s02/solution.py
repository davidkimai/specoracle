from typing import Any, Optional

TIMESTAMP_FIELD = "timestamp"


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    _validate_inputs(events, key_fields, window_seconds)

    retained_events: list[dict] = []
    kept_timestamps_by_key: dict[tuple[Any, ...], list[int]] = {}

    for event in events:
        if not _is_well_formed_event(event, key_fields):
            continue

        composite_key = _composite_key(event, key_fields)
        if composite_key is None:
            continue

        timestamp = event[TIMESTAMP_FIELD]
        kept_timestamps = kept_timestamps_by_key.setdefault(composite_key, [])

        if _is_duplicate(timestamp, kept_timestamps, window_seconds):
            continue

        retained_events.append(event)
        kept_timestamps.append(timestamp)

    return retained_events


def _validate_inputs(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    if not isinstance(key_fields, list):
        raise TypeError("key_fields must be a list of strings")

    if not all(isinstance(field, str) for field in key_fields):
        raise TypeError("key_fields must be a list of strings")

    if not _is_plain_integer(window_seconds):
        raise TypeError("window_seconds must be an integer")

    if window_seconds < 0:
        raise ValueError("window_seconds must be non-negative")


def _is_well_formed_event(event: Any, key_fields: list[str]) -> bool:
    if not isinstance(event, dict):
        return False

    if TIMESTAMP_FIELD not in event:
        return False

    if not _is_plain_integer(event[TIMESTAMP_FIELD]):
        return False

    return all(field in event for field in key_fields)


def _composite_key(event: dict, key_fields: list[str]) -> Optional[tuple[Any, ...]]:
    key = tuple(event[field] for field in key_fields)

    try:
        hash(key)
    except TypeError:
        return None

    return key


def _is_duplicate(
    timestamp: int,
    kept_timestamps: list[int],
    window_seconds: int,
) -> bool:
    return any(
        0 <= timestamp - kept_timestamp < window_seconds
        for kept_timestamp in kept_timestamps
    )


def _is_plain_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
