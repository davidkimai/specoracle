def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract fields from a nested record using dot-separated paths.

    Args:
        record: The source dictionary to extract from.
        paths: A mapping of output_key -> dot-separated path string.
        default: Value to use when a path cannot be resolved.

    Returns:
        A dictionary mapping each output key to the extracted value.
    """
    result = {}
    for output_key, path in paths.items():
        result[output_key] = _resolve_path(record, path, default)
    return result


def _resolve_path(data, path: str, default):
    """
    Resolve a dot-separated path against a nested data structure.

    Supports integer indexes for list access (e.g., "orders.0.total").
    """
    parts = path.split(".")
    current = data
    for part in parts:
        if current is None:
            return default
        if isinstance(current, list):
            try:
                index = int(part)
                current = current[index]
            except (ValueError, IndexError):
                return default
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                # Try integer key as well for dicts with integer keys
                try:
                    index = int(part)
                    if index in current:
                        current = current[index]
                    else:
                        return default
                except ValueError:
                    return default
        else:
            # Scalar value but more path segments remain
            return default
    return current
