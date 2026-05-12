from typing import Any


_MISSING = object()


def _resolve_path(record: dict, path: str) -> Any:
    current: Any = record

    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return _MISSING
            current = current[part]
        elif isinstance(current, list):
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

    for key, path in paths.items():
        value = _resolve_path(record, path)
        result[key] = default if value is _MISSING else value

    return result
