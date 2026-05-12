from bisect import bisect_right, insort

_TIMESTAMP_FIELD = "timestamp"
_MISSING = object()


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    _validate_arguments(events, key_fields, window_seconds)

    retained: list[dict] = []
    seen: list[tuple[tuple[object, ...], list[int]]] = []

    for event in events:
        parts = _event_parts(event, key_fields)
        if parts is None:
            continue

        timestamp, composite_key = parts
        timestamps = _timestamps_for_key(seen, composite_key)

        if timestamps is not None and _is_duplicate(timestamps, timestamp, window_seconds):
            continue

        if timestamps is None:
            timestamps = []
            seen.append((composite_key, timestamps))

        insort(timestamps, timestamp)
        retained.append(event)

    return retained


def _validate_arguments(
    events: object,
    key_fields: object,
    window_seconds: object,
) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list")

    if not isinstance(key_fields, list):
        raise TypeError("key_fields must be a list")

    if not all(isinstance(field, str) for field in key_fields):
        raise TypeError("key_fields must contain only strings")

    if not _is_integer(window_seconds):
        raise TypeError("window_seconds must be an integer")

    if window_seconds < 0:
        raise ValueError("window_seconds must be non-negative")


def _event_parts(
    event: object,
    key_fields: list[str],
) -> tuple[int, tuple[object, ...]] | None:
    if not isinstance(event, dict):
        return None

    timestamp = event.get(_TIMESTAMP_FIELD, _MISSING)
    if not _is_integer(timestamp):
        return None

    if any(field not in event for field in key_fields):
        return None

    composite_key = tuple(event[field] for field in key_fields)
    return timestamp, composite_key


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _timestamps_for_key(
    seen: list[tuple[tuple[object, ...], list[int]]],
    composite_key: tuple[object, ...],
) -> list[int] | None:
    for saved_key, timestamps in seen:
        if saved_key == composite_key:
            return timestamps
    return None


def _is_duplicate(
    timestamps: list[int],
    timestamp: int,
    window_seconds: int,
) -> bool:
    index = bisect_right(timestamps, timestamp)
    if index == 0:
        return False

    kept_timestamp = timestamps[index - 1]
    return timestamp - kept_timestamp < window_seconds
