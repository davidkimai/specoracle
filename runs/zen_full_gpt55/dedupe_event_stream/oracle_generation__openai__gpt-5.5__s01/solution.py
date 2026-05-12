"""Utilities for deduplicating event streams."""

from typing import Any, Optional

TIMESTAMP_FIELD = "timestamp"

CompositeKey = tuple[Any, ...]
KeptWindows = list[tuple[CompositeKey, list[int]]]


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    """Return events with duplicates removed within per-key timestamp windows."""
    _validate_arguments(events, key_fields, window_seconds)

    retained_events: list[dict] = []
    kept_windows: KeptWindows = []

    for event in events:
        parsed_event = _parse_event(event, key_fields)
        if parsed_event is None:
            continue

        timestamp, composite_key = parsed_event
        key_index = _find_key_index(kept_windows, composite_key)

        if key_index is None:
            kept_windows.append((composite_key, [timestamp]))
            retained_events.append(event)
            continue

        kept_timestamps = kept_windows[key_index][1]
        if _is_duplicate(timestamp, kept_timestamps, window_seconds):
            continue

        kept_timestamps.append(timestamp)
        retained_events.append(event)

    return retained_events


def _validate_arguments(
    events: object,
    key_fields: object,
    window_seconds: object,
) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list")

    if not isinstance(key_fields, list):
        raise TypeError("key_fields must be a list of strings")

    for field in key_fields:
        if not isinstance(field, str):
            raise TypeError("key_fields must be a list of strings")

    if isinstance(window_seconds, bool) or not isinstance(window_seconds, int):
        raise TypeError("window_seconds must be an integer")

    if window_seconds < 0:
        raise ValueError("window_seconds must be non-negative")


def _parse_event(
    event: object,
    key_fields: list[str],
) -> Optional[tuple[int, CompositeKey]]:
    if not isinstance(event, dict):
        return None

    timestamp = _timestamp_or_none(event)
    if timestamp is None:
        return None

    composite_key = _composite_key_or_none(event, key_fields)
    if composite_key is None:
        return None

    return timestamp, composite_key


def _timestamp_or_none(event: dict) -> Optional[int]:
    if TIMESTAMP_FIELD not in event:
        return None

    timestamp = event[TIMESTAMP_FIELD]
    if isinstance(timestamp, bool) or not isinstance(timestamp, int):
        return None

    return timestamp


def _composite_key_or_none(
    event: dict,
    key_fields: list[str],
) -> Optional[CompositeKey]:
    values: list[Any] = []

    for field in key_fields:
        if field not in event:
            return None
        values.append(event[field])

    return tuple(values)


def _find_key_index(
    kept_windows: KeptWindows,
    composite_key: CompositeKey,
) -> Optional[int]:
    for index, (existing_key, _) in enumerate(kept_windows):
        if existing_key == composite_key:
            return index

    return None


def _is_duplicate(
    timestamp: int,
    kept_timestamps: list[int],
    window_seconds: int,
) -> bool:
    for kept_timestamp in kept_timestamps:
        if kept_timestamp <= timestamp and timestamp - kept_timestamp < window_seconds:
            return True

    return False


__all__ = ["dedupe_events"]
