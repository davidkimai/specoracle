"""
json_path_projection.py

Provides extract_fields: project named dot-separated paths out of a nested
record into a flat output dictionary.
"""


def _step_into_list(current, part, default):
    """Advance into a list using *part* as an integer index."""
    try:
        index = int(part)
    except ValueError:
        return default, False
    if index < 0 or index >= len(current):
        return default, False
    return current[index], True


def _step_into_dict(current, part, default):
    """Advance into a dict using *part* as a string key, then integer key."""
    if part in current:
        return current[part], True
    try:
        int_part = int(part)
    except ValueError:
        return default, False
    if int_part in current:
        return current[int_part], True
    return default, False


def _step(current, part, default):
    """Advance one path segment into *current*."""
    if isinstance(current, list):
        return _step_into_list(current, part, default)
    if isinstance(current, dict):
        return _step_into_dict(current, part, default)
    return default, False


def _resolve_path(record, path, default):
    """Walk *path* (dot-separated) through *record*, return value or default."""
    current = record
    for part in path.split("."):
        current, ok = _step(current, part, default)
        if not ok:
            return default
    return current


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """
    Extract values from *record* using dot-separated *paths*.

    Parameters
    ----------
    record  : The source nested structure (dict at the top level).
    paths   : Mapping of output_key -> dot-separated path string.
    default : Value to use when a path cannot be resolved.

    Returns
    -------
    A new dict mapping each output key to its resolved (or default) value.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__!r}")

    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }
