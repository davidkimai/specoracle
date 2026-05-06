def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract fields from a nested record using dot-separated paths.

    Args:
        record: The source dictionary to extract from.
        paths: A mapping of output_key -> dot-separated path string.
        default: Value to use when a path cannot be resolved.

    Returns:
        A dictionary mapping each output key to the extracted (or default) value.
    """
    result = {}
    for output_key, path in paths.items():
        result[output_key] = _resolve_path(record, path, default)
    return result


def _resolve_path(data, path: str, default):
    """
    Traverse nested dicts/lists following a dot-separated path.
    Integer path segments are treated as list indexes.
    """
    if not path:
        return default

    segments = path.split(".")
    current = data

    for segment in segments:
        if current is None:
            return default

        # Try integer index first (for lists)
        if isinstance(current, list):
            try:
                index = int(segment)
                current = current[index]
            except (ValueError, IndexError):
                return default
        elif isinstance(current, dict):
            # Also handle the case where dict keys might be integer-like strings
            if segment in current:
                current = current[segment]
            else:
                # Try integer key as fallback
                try:
                    int_key = int(segment)
                    if int_key in current:
                        current = current[int_key]
                    else:
                        return default
                except ValueError:
                    return default
        else:
            # Current is a scalar but we still have segments to traverse
            return default

    return current
