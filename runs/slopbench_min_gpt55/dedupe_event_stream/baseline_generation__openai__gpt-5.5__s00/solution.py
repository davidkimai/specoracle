from typing import Any


__all__ = ["dedupe_events"]


def _is_integer_timestamp(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _find_timestamp_bucket(
    buckets: list[tuple[tuple[Any, ...], list[int]]],
    composite_key: tuple[Any, ...],
) -> list[int] | None:
    for existing_key, timestamps in buckets:
        if existing_key == composite_key:
            return timestamps
    return None


def _is_duplicate_timestamp(
    timestamp: int,
    kept_timestamps: list[int],
    window_seconds: int,
) -> bool:
    if window_seconds <= 0:
        return False

    for kept_timestamp in kept_timestamps:
        delta = timestamp - kept_timestamp
        if 0 <= delta < window_seconds:
            return True

    return False


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    retained: list[dict] = []
    buckets: list[tuple[tuple[Any, ...], list[int]]] = []

    if not isinstance(window_seconds, int) or isinstance(window_seconds, bool):
        return retained

    if not isinstance(key_fields, list) or any(
        not isinstance(field, str) for field in key_fields
    ):
        return retained

    if not isinstance(events, list):
        return retained

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        if not _is_integer_timestamp(timestamp):
            continue

        if any(field not in event for field in key_fields):
            continue

        composite_key = tuple(event[field] for field in key_fields)
        kept_timestamps = _find_timestamp_bucket(buckets, composite_key)

        if kept_timestamps is None:
            kept_timestamps = []
            buckets.append((composite_key, kept_timestamps))

        if _is_duplicate_timestamp(timestamp, kept_timestamps
