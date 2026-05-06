"""
json_path_projection.py

Provides extract_fields for projecting values out of nested dicts/lists
using dot-separated paths with optional integer list indexes.
"""


def _resolve_path(record, path, default):
    """Walk *path* segments into *record*, returning *default* on any miss."""
    node = record
    for segment in path.split("."):
        if node is None:
            return default
        if isinstance(node, list):
            try:
                index = int(segment)
            except ValueError:
                return default
            if index < 0 or index >= len(node):
                return default
            node = node[index]
        elif isinstance(node, dict):
            if segment not in node:
                return default
            node = node[segment]
        else:
            return default
    return node


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """
    Extract values from *record* according to *paths*.

    Parameters
    ----------
    record  : nested dict/list structure to query
    paths   : mapping of output_key -> dot-separated path string
    default : value to use when a path cannot be resolved

    Returns
    -------
    dict mapping each output key to the resolved (or default) value.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__}")

    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }
