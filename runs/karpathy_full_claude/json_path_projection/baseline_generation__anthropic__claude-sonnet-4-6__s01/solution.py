"""
json_path_projection.py

Provides extract_fields(record, paths, default=None) for dot-separated path
projection over nested dicts and lists.
"""

from typing import Any


def _resolve_path(record: Any, path: str, default: Any) -> Any:
    """
    Walk *record* following the dot-separated *path*.

    Each segment is tried as a dict key first; if the current node is a list
    and the segment is a valid integer index, list indexing is used instead.
    Returns *default* if any segment cannot be resolved.
    """
    parts = path.split(".")
    current = record
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
            # Scalar node — cannot descend further
            return default
    return current


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """
    Extract values from *record* according to *paths*.

    Parameters
    ----------
    record  : The source nested structure (dict).
    paths   : Mapping of output_key -> dot-separated path string.
    default : Value to use when a path cannot be resolved.

    Returns
    -------
    dict mapping each output key to the resolved (or default) value.
    The input *record* is never mutated.
    """
    result = {}
    for output_key, path in paths.items():
        result[output_key] = _resolve_path(record, path, default)
    return result
