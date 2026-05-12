from typing import Any


__all__ = ["extract_fields"]


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    """Extract values from a nested dictionary/list record using dot-separated paths."""
    _require_dict(record, "record")
    _require_dict(paths, "paths")

    result = {}
    for output_key, path in paths.items():
        _require_string(output_key, "paths key")
        segments = _split_path(path)
        result[output_key] = _resolve_path(record, segments, default)

    return result


def _require_dict(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _require_string(value: Any, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a str")


def _split_path(path: Any) -> list[str]:
    _require_string(path, "path")

    if path == "":
        raise ValueError("path must not be empty")

    segments = path.split(".")
    if any(segment == "" for segment in segments):
        raise ValueError(f"path contains an empty segment: {path!r}")

    return segments


def _resolve_path(record: dict, segments: list[str], default: Any) -> Any:
    current: Any = record

    for segment in segments:
        if isinstance(current, dict):
            if segment not in current:
                return default
            current = current[segment]
            continue

        if isinstance(current, list):
            index = _parse_list_index(segment)
            if index is None or index >= len(current):
                return default
            current = current[index]
            continue

        return default

    return current


def _parse_list_index(segment: str) -> int | None:
    if not segment.isdecimal():
        return None

    return int(segment)
