def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    result = {}
    for key, path in paths.items():
        parts = path.split('.')
        current = record
        try:
            for part in parts:
                if isinstance(current, list):
                    current = current[int(part)]
                elif isinstance(current, dict):
                    current = current[part]
                else:
                    current = default
                    break
            result[key] = current
        except (KeyError, IndexError, ValueError, TypeError):
            result[key] = default
    return result
