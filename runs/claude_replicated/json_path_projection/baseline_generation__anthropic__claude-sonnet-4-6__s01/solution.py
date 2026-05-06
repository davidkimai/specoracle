def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract fields from a nested record using dot-separated paths.

    Args:
        record: The source dictionary to extract values from.
        paths: A mapping of output_key -> dot-separated path string.
        default: Value to use when a path cannot be resolved.

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

            # Try integer index for list access
            try:
                index = int(part)
                if isinstance(current, (list, tuple)):
                    try:
                        current = current[index]
                    except IndexError:
                        resolved = False
                        break
                elif isinstance(current, dict):
                    # Key might literally be an integer string
                    if part in current:
                        current = current[part]
                    else:
                        resolved = False
                        break
                else:
                    resolved = False
                    break
            except ValueError:
                # Not an integer, treat as dict key
                if isinstance(current, dict):
                    if part in current:
                        current = current[part]
                    else:
                        resolved = False
                        break
                else:
                    resolved = False
                    break

        result[output_key] = current if resolved else default

    return result
