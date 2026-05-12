def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    result = {}
    for key, path in paths.items():
        parts = path.split(".")
        value = record
        try:
            for part in parts:
                if isinstance(value, list):
                    value = value[int(part)]
                elif isinstance(value, dict):
                    value = value[part]
                else:
                    value = default
                    break
        except (KeyError, IndexError, ValueError, TypeError):
            value = default
        result[key] = value
    return result
