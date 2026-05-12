def merge_policy(defaults: dict, override: dict) -> dict:
    result = {}
    for key, value in defaults.items():
        if key not in override:
            result[key] = value
        elif override[key] is None:
            pass
        elif isinstance(value, dict) and isinstance(override[key], dict):
            result[key] = merge_policy(value, override[key])
        else:
            result[key] = override[key]
    for key, value in override.items():
        if key not in defaults and value is not None:
            result[key] = value
    return result
