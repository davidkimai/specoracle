"""
json_path_projection.py

Provides extract_fields for projecting values out of nested dicts/lists
using dot-separated paths with optional integer list indexes.
"""


def _step_into_list(current, segment, default):
    """Descend one segment into a list, returning default on any error."""
    try:
        index = int(segment)
    except ValueError:
        return default, True
    if index < 0 or index >= len(current):
        return default, True
    return current[index], False


def _step_into_dict(current, segment, default):
    """Descend one segment into a dict, returning default on miss."""
    if segment not in current:
        return default, True
    return current[segment], False


def _step(current, segment, default):
    """Advance one path segment, returning (value, exhausted) pair."""
    if isinstance(current, list):
        return _step_into_list(current, segment, default)
    if isinstance(current, dict):
        return _step_into_dict(current, segment, default)
    return default, True


def _resolve_path(record, path, default):
    """Walk *path* segments into *record*, returning *default* on any miss."""
    current = record
    for segment in path.split("."):
        current, done = _step(current, segment, default)
        if done:
            return default
    return current


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """
    Project fields out of *record* according to *paths*.

    Parameters
    ----------
    record  : The source nested structure (dict at the top level).
    paths   : Mapping of output_key -> dot-separated path string.
    default : Value to use when a path cannot be resolved.

    Returns
    -------
    A new dict mapping each output key to the resolved (or default) value.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__!r}")

    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }
