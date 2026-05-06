"""
json_path_projection.py

Provides extract_fields: extract values from a nested dict/list structure
using dot-separated paths with optional integer list indexes.
"""


def _resolve_path(record, path, default):
    """Walk *record* along *path* (dot-separated) and return the value found,
    or *default* if any step cannot be resolved."""
    current = record
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return default
            if index < 0 or index >= len(current):
                return default
            current = current[index]
        else:
            return default
    return current


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """Return a dict mapping each key in *paths* to the value found in *record*
    by following the corresponding dot-separated path.

    Parameters
    ----------
    record:
        The source nested structure (dict at the top level).
    paths:
        Mapping of output-key -> dot-separated path string.
    default:
        Value to use when a path cannot be resolved.

    Returns
    -------
    dict
        New dict with the same keys as *paths*, each holding the resolved value
        or *default*.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__!r}")

    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }
