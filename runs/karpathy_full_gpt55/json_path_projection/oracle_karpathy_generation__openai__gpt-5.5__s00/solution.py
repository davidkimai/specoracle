_MISSING = object()


def _resolve_path(record, path):
    current = record

    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return _MISSING
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return _MISSING

            try:
                current = current[index]
            except IndexError:
                return _MISSING
        else:
            return _MISSING

    return current


def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    result = {}

    for key, path in paths.items():
        value = _resolve_path(record, path)
        result[key] = default if value is _MISSING else value

    return result
