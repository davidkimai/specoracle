from __future__ import annotations

from typing import Any


_MISSING = object()


def _parse_index(component: str) -> int | None:
    """Return an integer list index for a path component, or None if invalid."""
    if not component:
        return None

    start = 1 if component[0] in "+-" else 0
    if start == len(component) or not component[start:].isdigit():
        return None

    return int(component)


def _resolve_path(record: dict, path: str) -> Any:
    """Resolve a dot-separated path against a record, returning _MISSING on failure."""
    current: Any = record

    for component in path.split("."):
        if isinstance(current, dict):
            if component not in current:
                return _MISSING
            current = current[component]
        elif isinstance(current, list):
            index = _parse_index(component)
            if index is None:
                return _MISSING
            try:
                current = current[index]
            except IndexError:
                return _MISSING
        else:
            return _MISSING

    return current


def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract values from a nested dictionary/list record using dot-separated paths.

    Each item in `paths` maps an output key to a path such as "orders.0.total".
    If a path cannot be resolved, the output value is `default`.
    """
    result = {}

    for output_key, path in paths.items():
        value = _resolve_path(record, path)
        result[output_key] = default if value is _MISSING else value

    return result
