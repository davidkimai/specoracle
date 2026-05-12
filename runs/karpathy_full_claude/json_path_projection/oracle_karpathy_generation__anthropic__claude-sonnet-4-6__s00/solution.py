def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    result = {}
    for key, path in paths.items():
        parts = path.split(".")
        current = record
        for part in parts:
            try:
                if isinstance(current, list):
                    current = current[int(part)]
                elif isinstance(current, dict):
                    current = current[part]
                else:
                    current = default
                    break
            except (KeyError, IndexError, ValueError, TypeError):
                current = default
                break
        result[key] = current
    return result
