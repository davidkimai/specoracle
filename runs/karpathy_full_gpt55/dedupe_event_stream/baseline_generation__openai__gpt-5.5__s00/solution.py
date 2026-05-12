__all__ = ["dedupe_events"]


_MISSING = object()


def _is_integer_timestamp(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _composite_key(event: dict, key_fields: list[str]) -> tuple[object, ...] | object:
    try:
        return tuple(event[field] for field in key_fields)
    except (KeyError, TypeError):
        return _MISSING


def _is_duplicate_timestamp(
    timestamp: int, kept_timestamps: list[int], window_seconds: int
) -> bool:
    if window_seconds <= 0:
        return False

    for kept_timestamp in kept_timestamps:
        if kept_timestamp <= timestamp and timestamp - kept_timestamp < window_seconds:
            return True
    return False


def _find_unhashable_key_windows(
    records: list[tuple[tuple[object, ...], list[int]]],
    composite_key: tuple[object, ...],
) -> list[int] | None:
    for existing_key, kept_timestamps in records:
        try:
            if existing_key == composite_key:
                return kept_timestamps
        except Exception:
            continue
    return None


def dedupe_events(
    events: list[dict], key_fields: list[str], window_seconds: int
) -> list[dict]:
    """
    Retain the first well-formed event for each composite key within each
    timestamp window.

    An event is well-formed when it is a dictionary, has an integer
    ``timestamp`` field, and contains every field named in ``key_fields``.
    Malformed events are ignored.
    """
    retained: list[dict] = []

    hashable_windows: dict[tuple[object, ...], list[int]] = {}
    unhashable_windows: list[tuple[tuple[object, ...], list[int]]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp", _MISSING)
        if not _is_integer_timestamp(timestamp):
            continue

        composite_key = _composite_key(event, key_fields)
        if composite_key is _MISSING:
            continue

        try:
            kept_timestamps = hashable_windows.get(composite_key)
        except TypeError:
            kept_timestamps = _find_unhashable_key_windows(
                unhashable_windows, composite_key
            )
            if kept_timestamps is None:
                kept_timestamps = []
                unhashable_windows.append((composite_key, kept_timestamps))
        else:
            if kept_timestamps is None:
                kept_timestamps = []
                hashable_windows[composite_key] = kept_timestamps

        if _is_duplicate_timestamp(timestamp, kept_timestamps, window_seconds):
            continue

        retained.append(event)
        kept_timestamps.append(timestamp)

    return retained
