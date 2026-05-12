from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_MISSING = object()


def _resolve_path(record: Any, path: str) -> Any:
    current = record

    for part in path.split("."):
        if isinstance(current, Mapping):
            if part not in current:
                return _MISSING
            current = current[part]
        elif isinstance(current, (list, tuple)):
            if not part.isdigit():
                return _MISSING
            index = int(part)
            if index >= len(current):
                return _MISSING
            current = current[index]
        else:
            return _MISSING

    return current


def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    result = {}

    for output_key, path in paths.items():
        if not isinstance(path, str):
            result[output_key] = default
            continue

        value = _resolve_path(record, path)
        result[output_key] = default if value is _MISSING else value

    return result
