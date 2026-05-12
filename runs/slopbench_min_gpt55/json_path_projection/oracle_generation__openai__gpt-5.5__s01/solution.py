from typing import Any


_MISSING = object()


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    if not isinstance(paths, dict):
        raise TypeError("paths must be a dict")

    result = {}
    for output_key, path in paths.items():
        _validate_path_item(output_key, path)
        result[output_key] = _resolve_path(record, _split_path(path), default)

    return result


def _validate_path_item(output_key: object, path: object) -> None:
    if not isinstance(output_key, str):
        raise TypeError("all output keys in paths must be strings")
    if not isinstance(path, str):
        raise TypeError("all path values in paths must be strings")


def _split_path(path: str) -> list[str]:
    if path == "":
        raise ValueError("path must not be empty")

    parts = path.split(".")
    if any(part == "" for part in parts):
        raise ValueError(f"path contains an empty segment: {path!r}")

    return parts


def _resolve_path(record: dict, parts: list[str], default: Any) -> Any:
    current: Any = record

    for part in parts:
        current = _resolve_part(current, part)
        if current is _MISSING:
            return default

    return current


def _resolve_part(value: Any, part: str) -> Any:
    if isinstance(value, dict):
        return value.get(part, _MISSING)

    if isinstance(value, list):
        index = _parse_list_index(part)
        if index is _MISSING:
            return _MISSING
        if not -len(value) <= index < len(value):
            return _MISSING
        return value[index]

    return _MISSING


def _parse_list_index(part: str) -> int | object:
    try:
        return int(part)
    except ValueError:
        return _MISSING
