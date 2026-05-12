from __future__ import annotations

from typing import Any, Mapping


_MISSING = object()


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    """
    Extract values from a nested dictionary/list record using dot-separated paths.

    Path components are dictionary keys when traversing dictionaries and integer
    indexes when traversing lists. If any component cannot be resolved, the
    provided default value is used for that output key.

    Example:
        extract_fields(
            {"orders": [{"total": 12.5}]},
            {"first_total": "orders.0.total"},
        )
        -> {"first_total": 12.5}
    """
    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }


def _resolve_path(record: Any, path: str, default: Any) -> Any:
    if not isinstance(path, str):
        return default

    current = record

    for part in path.split("."):
        current = _descend(current, part)
        if current is _MISSING:
            return default

    return current


def _descend(current: Any, part: str) -> Any:
    if isinstance(current, Mapping):
        return current.get(part, _MISSING)

    if isinstance(current, list):
        index = _parse_non_negative_int(part)
        if index is None or index >= len(current):
            return _MISSING
        return current[index]

    return _MISSING


def _parse_non_negative_int(value: str) -> int | None:
    if not value or not value.isdecimal():
        return None
    return int(value)
