def _resolve_path(record, path, default):
    parts = path.split(".")
    current = record
    for part in parts:
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return default
            if index < 0 or index >= len(current):
                return default
            current = current[index]
        elif isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        else:
            return default
    return current


def extract_fields(record: dict, paths: dict, default=None) -> dict:
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__}")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dict, got {type(paths).__name__}")
    return {
        output_key: _resolve_path(record, path, default)
        for output_key, path in paths.items()
    }
