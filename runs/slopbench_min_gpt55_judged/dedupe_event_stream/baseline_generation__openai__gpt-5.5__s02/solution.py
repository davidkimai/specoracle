from __future__ import annotations

from collections.abc import Hashable
from typing import Any


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    retained: list[dict] = []
    last_kept_timestamp_by_key: dict[tuple[Any, ...], int] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue

        if any(field not in event for field in key_fields):
            continue

        composite_key = tuple(event[field] for field in key_fields)
        if not all(isinstance(value, Hashable) for value in composite_key):
            continue

        last_kept_timestamp = last_kept_timestamp_by_key.get(composite_key)
        if last_kept_timestamp is not None:
            if timestamp - last_kept_timestamp < window_seconds:
                continue

        retained.append(event)
        last_kept_timestamp_by_key[composite_key] = timestamp

    return retained
