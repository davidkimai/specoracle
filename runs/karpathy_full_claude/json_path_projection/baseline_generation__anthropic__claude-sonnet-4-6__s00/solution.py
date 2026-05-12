"""
json_path_projection.py

Provides extract_fields(record, paths, default=None) for dot-separated path
projection over nested dicts/lists.
"""

from __future__ import annotations

from typing import Any


def _resolve_path(data: Any, parts: list[str], default: Any) -> Any:
    """
    Walk *data* following *parts* (already split on '.').
    Returns *default* if any step fails.
    """
    current = data
    for part in parts:
        if current is None:
            return default
        if isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        elif isinstance(current, (list, tuple)):
            try:
                index = int(part)
            except ValueError:
                return default
            try:
                current = current[index]
            except IndexError:
                return default
        else:
            # Scalar value — cannot descend further
            return default
    return current


def extract_fields(
    record: dict,
    paths: dict[str, str],
    default: Any = None,
) -> dict:
    """
    Extract values from *record* using dot-separated *paths*.

    Parameters
    ----------
    record:
        The source nested structure (dict at the top level).
    paths:
        Mapping of output_key -> dot-separated path string.
        Integer segments are treated as list indexes.
    default:
        Value used when a path cannot be resolved.

    Returns
    -------
    dict
        {output_key: extracted_value_or_default, ...}
    """
    result: dict[str, Any] = {}
    for output_key, path in paths.items():
        if not isinstance(path, str) or path == "":
            result[output_key] = default
            continue
        parts = path.split(".")
        result[output_key] = _resolve_path(record, parts, default)
    return result
