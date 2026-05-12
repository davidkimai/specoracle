from typing import Any

__all__ = ["extract_fields"]

_UNRESOLVED = object()


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    if not isinstance(paths, dict):
        raise TypeError("paths must be a dict mapping output keys to path strings")

    result = {}
    for output_key, path in paths.items():
        if not isinstance(output_key, str):
            raise TypeError("all output keys in paths must be strings")
        parts = _split_path(path)
        value = _resolve_path(record, parts)
        result[output_key] = default if value is _UNRESOLVED else value

    return result


def _split_path(path: str) -> list[str]:
    if not isinstance(path, str):
        raise TypeError("each path must be a string")
    if path == "":
        raise ValueError("path must not be empty")

    parts = path.split(".")
    if any(part == "" for part in parts):
        raise ValueError(f"path contains an empty segment: {path!r}")

    return parts


def _resolve_path(value: Any, parts: list[str]) -> Any:
    current = value

    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return _UNRESOLVED
            current = current[part]
            continue

        if isinstance(current, list):
            index = _list_index(part)
            if index is None or index >= len(current):
                return _UNRESOLVED
            current = current[index]
            continue

        return _UNRESOLVED

    return current


def _list_index(part: str) -> int | None:
    if not part.isdecimal():
        return None
    return int(part)
