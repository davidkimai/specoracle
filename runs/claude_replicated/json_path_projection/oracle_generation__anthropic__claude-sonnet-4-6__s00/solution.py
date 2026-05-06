"""
json_path_projection.py

Provides extract_fields for projecting values out of nested dicts/lists
using dot-separated paths with optional integer list indexes.
"""


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


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """
    Extract values from *record* using dot-separated *paths*.

    Parameters
    ----------
    record  : source dictionary (not mutated)
    paths   : mapping of output_key -> dot-separated path string
    default : value used when a path cannot be resolved

    Returns
    -------
    dict mapping each output key to the resolved (or default) value.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__!r}")

    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }
