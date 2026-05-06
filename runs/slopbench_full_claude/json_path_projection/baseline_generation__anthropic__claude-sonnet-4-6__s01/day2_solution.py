def extract_fields(
    record: dict,
    paths: dict[str, str],
    default=None,
    required: set | None = None,
) -> dict:
    """
    Extract fields from a nested record using dot-separated paths.

    Args:
        record: The source dictionary to extract from.
        paths: A mapping of output_key -> dot-separated path string.
        default: Value to use when a path cannot be resolved.
        required: A set of output keys for which a missing path raises KeyError
                  instead of returning default.

    Returns:
        A dictionary mapping each output key to the extracted (or default) value.

    Raises:
        KeyError: If an output key is in `required` and its path cannot be resolved.
    """
    _sentinel = object()
    result = {}
    for output_key, path in paths.items():
        value = _resolve_path(record, path, _sentinel)
        if value is _sentinel:
            if required is not None and output_key in required:
                raise KeyError(output_key)
            value = default
        result[output_key] = value
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
