from __future__ import annotations

from typing import Any

_MISSING = object()

_TAG_ATOM = object()
_TAG_DICT = object()
_TAG_LIST = object()
_TAG_TUPLE = object()
_TAG_SET = object()
_TAG_FROZENSET = object()


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _freeze_for_key(value: Any, seen: set[int]) -> Any:
    if isinstance(value, dict):
        object_id = id(value)
        if object_id in seen:
            raise TypeError("cyclic key field value")
        seen.add(object_id)
        try:
            return (
                _TAG_DICT,
                frozenset(
                    (_freeze_for_key(item_key, seen), _freeze_for_key(item_value, seen))
                    for item_key, item_value in value.items()
                ),
            )
        finally:
            seen.remove(object_id)

    if isinstance(value, list):
        object_id = id(value)
        if object_id in seen:
            raise TypeError("cyclic key field value")
        seen.add(object_id)
        try:
            return (_TAG_LIST, tuple(_freeze_for_key(item, seen) for item in value))
        finally:
            seen.remove(object_id)

    if isinstance(value, tuple):
        object_id = id(value)
        if object_id in seen:
            raise TypeError("cyclic key field value")
        seen.add(object_id)
        try:
            return (_TAG_TUPLE, tuple(_freeze_for_key(item, seen) for item in value))
        finally:
            seen.remove(object_id)

    if isinstance(value, set):
        object_id = id(value)
        if object_id in seen:
            raise TypeError("cyclic key field value")
        seen.add(object_id)
        try:
            return (_TAG_SET, frozenset(_freeze_for_key(item, seen) for item in value))
        finally:
            seen.remove(object_id)

    if isinstance(value, frozenset):
        object_id = id(value)
        if object_id in seen:
            raise TypeError("cyclic key field value")
        seen.add(object_id)
        try:
            return (
                _TAG_FROZENSET,
                frozenset(_freeze_for_key(item, seen) for item in value),
            )
        finally:
            seen.remove(object_id)

    try:
        hash(value)
    except Exception as exc:
        raise TypeError("unhashable key field value") from exc

    return (_TAG_ATOM, value)


def _build_composite_key(event: dict, key_fields: tuple[str, ...]) -> Any:
    parts = []

    for field in key_fields:
        if field not in event:
            return _MISSING
        parts.append(_freeze_for_key(event[field], set()))

    return tuple(parts)


def dedupe_events(
    events: list[dict], key_fields: list[str], window_seconds: int
) -> list[dict]:
    if not _is_integer(window_seconds):
        raise TypeError("window_seconds must be an integer")

    fields = tuple(key_fields)
    if any(not isinstance(field, str) for field in fields):
        raise TypeError("key_fields must contain only strings")

    retained: list[dict] = []
    last_kept_timestamp_by_key: dict[Any, int] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp", _MISSING)
        if not _is_integer(timestamp):
            continue

        try:
            composite_key = _build_composite_key(event, fields)
        except Exception:
            continue

        if composite_key is _MISSING:
            continue

        if window_seconds > 0:
            try:
                last_timestamp = last_kept_timestamp_by_key.get(
                    composite_key, _MISSING
                )
            except Exception:
                continue

            if (
                last_timestamp is not _MISSING
                and timestamp - last_timestamp < window_seconds
            ):
                continue

        retained.append(event)

        try:
            last_kept_timestamp_by_key[composite_key] = timestamp
        except Exception:
            retained.pop()

    return retained


__all__ = ["dedupe_events"]
