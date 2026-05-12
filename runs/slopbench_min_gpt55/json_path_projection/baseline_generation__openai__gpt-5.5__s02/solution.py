from __future__ import annotations

_MISSING = object()


def _is_ascii_nonnegative_integer(text: str) -> bool:
    return bool(text) and all("0" <= char <= "9" for char in text)


def _resolve_path(record: dict, path: str):
    if not isinstance(path, str):
        return _MISSING

    current = record

    for segment in path.split("."):
        if isinstance(current, dict):
            if segment not in current:
                return _MISSING
            current = current[segment]
        elif isinstance(current, list):
            if not _is_ascii_nonnegative_integer(segment):
                return _MISSING

            index = int(segment)
            if index >= len(current):
                return _MISSING

            current = current[index]
        else:
            return _MISSING

    return current


def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract values from a nested dictionary/list structure using dot-separated paths.

    Dictionary components are resolved as string keys. List components must be
    non-negative integer indexes written as decimal digits.
    """
    result = {}

    for output_key, path in paths.items():
        value = _resolve_path(record, path)
        result[output_key] = default if value is _MISSING else value

    return result


__all__ = ["extract_fields"]
