from __future__ import annotations

from collections.abc import Mapping
from typing import Any

__all__ = ["extract_fields"]

_MISSING = object()


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    if not isinstance(record, Mapping):
        raise TypeError("record must be a dict or mapping")

    normalized_paths = _normalize_paths(paths)
    result = {}

    for output_key, segments in normalized_paths:
        value = _resolve_path(record, segments)
        result[output_key] = default if value is _MISSING else value

    return result


def _normalize_paths(paths: dict[str, str]) -> list[tuple[str, tuple[str, ...]]]:
    if not isinstance(paths, Mapping):
        raise TypeError("paths must be a dict or mapping")

    normalized = []

    for output_key, path in paths.items():
        if not isinstance(output_key, str):
            raise TypeError("all output keys in paths must be strings")
        if not isinstance(path, str):
            raise TypeError(f"path for output key {output_key!r} must be a string")

        normalized.append((output_key, _split_path(path, output_key)))

    return normalized


def _split_path(path: str, output_key: str) -> tuple[str, ...]:
    if path == "":
        raise ValueError(f"path for output key {output_key!r} must not be empty")

    segments = tuple(path.split("."))

    if any(segment == "" for segment in segments):
        raise ValueError(
            f"path for output key {output_key!r} must not contain empty segments"
        )

    return segments


def _resolve_path(record: Mapping, segments: tuple[str, ...]) -> Any:
    current = record

    for segment in segments:
        if isinstance(current, Mapping):
            if segment not in current:
                return _MISSING
            current = current[segment]
            continue

        if isinstance(current, list):
            index = _list_index(segment)
            if index is _MISSING or index >= len(current):
                return _MISSING
            current = current[index]
            continue

        return _MISSING

    return current


def _list_index(segment: str) -> int | object:
    try:
        index = int(segment, 10)
    except ValueError:
        return _MISSING

    if index < 0:
        return _MISSING

    return index
