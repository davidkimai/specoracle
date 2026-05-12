from typing import Any


_MISSING = object()


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    """Extract values from a nested record using dot-separated paths."""
    _validate_inputs(record, paths)

    return {
        output_key: _value_or_default(record, path, default)
        for output_key, path in paths.items()
    }


def _validate_inputs(record: dict, paths: dict[str, str]) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    if not isinstance(paths, dict):
        raise TypeError("paths must be a dict")

    for output_key, path in paths.items():
        if not isinstance(output_key, str):
            raise TypeError("all paths keys must be strings")

        if not isinstance(path, str):
            raise TypeError("all paths values must be strings")

        _validate_path(path)


def _validate_path(path: str) -> None:
    if path == "":
        raise ValueError("path must not be empty")

    if path.startswith(".") or path.endswith(".") or ".." in path:
        raise ValueError(f"path has an empty component: {path!r}")


def _value_or_default(record: dict, path: str, default: Any) -> Any:
    value = _resolve_path(record, path)
    if value is _MISSING:
        return default
    return value


def _resolve_path(record: dict, path: str) -> Any:
    current: Any = record

    for part in path.split("."):
        current = _resolve_part(current, part)
        if current is _MISSING:
            return _MISSING

    return current


def _resolve_part(value: Any, part: str) -> Any:
    if isinstance(value, dict):
        return value.get(part, _MISSING)

    if isinstance(value, list):
        return _list_value_at(value, part)

    return _MISSING


def _list_value_at(values: list, index_text: str) -> Any:
    if not index_text.isdecimal():
        return _MISSING

    index = int(index_text)
    if index >= len(values):
        return _MISSING

    return values[index]
