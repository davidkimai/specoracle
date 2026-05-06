"""
json_path_projection.py

Provides extract_fields for projecting values out of nested dicts/lists
using dot-separated paths with optional integer list indexes.
"""

_SENTINEL = object()


def _resolve_path(data, path: str, default):
    """Walk *data* following the dot-separated *path*; return *default* on failure."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return default
            try:
                current = current[index]
            except IndexError:
                return default
        elif isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        else:
            return default
    return current


def extract_fields(record: dict, paths: dict, default=None, required=None) -> dict:
    """
    Extract values from *record* using dot-separated *paths*.

    Parameters
    ----------
    record   : source dictionary (not mutated)
    paths    : mapping of output_key -> dot-separated path string
    default  : value used when a path cannot be resolved
    required : optional set of output keys whose paths must resolve;
               if a required path cannot be resolved, KeyError is raised
               for that output key instead of returning default

    Returns
    -------
    dict mapping each output key to the resolved (or default) value.

    Raises
    ------
    KeyError  : if an output key is in *required* and its path cannot be resolved
    TypeError : if *record* or *paths* are not dicts
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__!r}")

    required_keys = set(required) if required is not None else set()

    result = {}
    for output_key, path in paths.items():
        value = _resolve_path(record, path, _SENTINEL)
        if value is _SENTINEL:
            if output_key in required_keys:
                raise KeyError(output_key)
            value = default
        result[output_key] = value
    return result
