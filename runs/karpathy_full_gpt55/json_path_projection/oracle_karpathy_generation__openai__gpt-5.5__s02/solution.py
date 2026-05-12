def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract values from a nested record using dot-separated paths.

    Dictionary segments are resolved as string keys. List segments must be valid
    integer indexes. If any segment cannot be resolved, the output value is
    default.
    """
    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }


def _resolve_path(record: dict, path: str, default):
    current = record

    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return default

            try:
                current = current[index]
            except IndexError:
                return default
        else:
            return default

    return current
