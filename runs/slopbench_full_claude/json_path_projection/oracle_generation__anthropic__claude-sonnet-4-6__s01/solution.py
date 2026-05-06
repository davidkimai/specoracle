"""
json_path_projection.py

Provides extract_fields for projecting values out of nested dicts/lists
using dot-separated paths with optional integer list indexes.
"""


def _resolve_path(data, segments, default):
    """Walk *segments* through *data*, returning default on any miss."""
    current = data
    for segment in segments:
        if isinstance(current, dict):
            if segment not in current:
                return default
            current = current[segment]
        elif isinstance(current, list):
            try:
                index = int(segment)
            except ValueError:
                return default
            if index < 0 or index >= len(current):
                return default
            current = current[index]
        else:
            return default
    return current


def _parse_segment(raw_segment):
    """Return the segment as an int if it looks like one, else as a str."""
    try:
        return str(int(raw_segment))  # normalise, but keep as str for dict lookup
    except ValueError:
        return raw_segment


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    """
    Extract values from *record* according to *paths*.

    Parameters
    ----------
    record  : nested dict (possibly containing lists)
    paths   : mapping of output_key -> dot-separated path string
    default : value returned when a path cannot be resolved

    Returns
    -------
    dict mapping each output key to its resolved value or *default*.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__!r}")

    result = {}
    for output_key, path in paths.items():
        if not isinstance(path, str):
            raise TypeError(
                f"path for key {output_key!r} must be a str, got {type(path).__name__!r}"
            )
        segments = path.split(".")
        result[output_key] = _resolve_path(record, segments, default)
    return result
