from __future__ import annotations

from typing import Any


_MISSING = object()


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    """Extract values from a nested dictionary/list record using dot paths."""
    _validate_record(record)
    _validate_paths(paths)

    result = {}
    for output_key, path in paths.items():
        value = _resolve_path(record, _split_path(path))
        result[output_key] = default if value is _MISSING else value

    return result


def _validate_record(record: dict) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")


def _validate_paths(paths: dict[str, str]) -> None:
    if not isinstance(paths, dict):
        raise TypeError("paths must be a dict")

    for output_key, path in paths.items():
        if not isinstance(output_key, str):
            raise TypeError("paths keys must be strings")
        if not isinstance(path, str):
            raise TypeError(f"path for output key {output_key!r} must be a string")


def _split_path(path: str) -> tuple[str, ...]:
    if path == "":
        raise ValueError("path must not be empty")

    parts = tuple(path.split("."))
    if any(part == "" for part in parts):
        raise ValueError(f"path contains an empty segment: {path!r}")

    return parts


def _resolve_path(record: dict, parts: tuple[str, ...]) -> Any:
    current: Any = record

    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return _MISSING
            current = current[part]
            continue

        if isinstance(current, list):
            index = _parse_list_index(part)
            if index is None or index >= len(current):
                return _MISSING
            current = current[index]
            continue

        return _MISSING

    return current


def _parse_list_index(part: str) -> int | None:
    if not part.isdecimal():
        return None

    return int(part)
