def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract fields from a nested record using dot-separated paths.
    
    Args:
        record: The source dictionary to extract from.
        paths: A mapping of output_key -> dot-separated path string.
        default: Value to use when a path cannot be resolved.
    
    Returns:
        A dictionary mapping each output key to its extracted value.
    """
    result = {}
    
    for output_key, path in paths.items():
        value = _resolve_path(record, path, default)
        result[output_key] = value
    
    return result


def _resolve_path(record, path: str, default):
    """
    Resolve a dot-separated path in a nested structure.
    
    Supports dict key access and integer list indexes.
    """
    if not path:
        return default
    
    parts = path.split(".")
    current = record
    
    for part in parts:
        if current is None:
            return default
        
        # Try integer index first (for list access)
        if isinstance(current, list):
            try:
                index = int(part)
                current = current[index]
            except (ValueError, IndexError, TypeError):
                return default
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                # Also try integer key in case dict has integer keys
                try:
                    index = int(part)
                    if index in current:
                        current = current[index]
                    else:
                        return default
                except (ValueError, TypeError):
                    return default
        else:
            # Current is a scalar but we still have path parts to traverse
            return default
    
    return current
