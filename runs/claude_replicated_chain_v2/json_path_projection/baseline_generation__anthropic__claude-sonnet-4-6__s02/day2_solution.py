def extract_fields(record: dict, paths: dict[str, str], default=None, required: set | None = None) -> dict:
    """
    Extract fields from a nested record using dot-separated paths.

    Args:
        record: The source dictionary to extract values from.
        paths: A mapping of output_key -> dot-separated path string.
        default: Value to use when a path cannot be resolved.
        required: A set of output keys that must be resolved; if not, raise KeyError.

    Returns:
        A dictionary mapping each output key to the extracted (or default) value.
    """
    result = {}
    for output_key, path in paths.items():
        parts = path.split(".")
        current = record
        resolved = True
        for part in parts:
            if current is None:
                resolved = False
                break
            # Try integer index first (for lists)
            try:
                index = int(part)
                if isinstance(current, (list, tuple)):
                    try:
                        current = current[index]
                    except IndexError:
                        resolved = False
                        break
                elif isinstance(current, dict):
                    # The key might literally be an integer string
                    if part in current:
                        current = current[part]
                    else:
                        resolved = False
                        break
                else:
                    resolved = False
                    break
            except ValueError:
                # Not an integer, treat as a dict key
                if isinstance(current, dict):
                    if part in current:
                        current = current[part]
                    else:
                        resolved = False
                        break
                else:
                    resolved = False
                    break
        if not resolved and required is not None and output_key in required:
            raise KeyError(output_key)
        result[output_key] = current if resolved else default
    return result
