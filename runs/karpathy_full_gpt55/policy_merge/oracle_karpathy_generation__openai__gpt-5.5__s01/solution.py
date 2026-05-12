def _copy_default_value(value):
    if isinstance(value, dict):
        return {key: _copy_default_value(child) for key, child in value.items()}
    return value


def merge_policy(defaults: dict, override: dict) -> dict:
    result = {key: _copy_default_value(value) for key, value in defaults.items()}

    for key, value in override.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict):
            base = result.get(key)
            if isinstance(base, dict):
                result[key] = merge_policy(base, value)
            else:
                result[key] = merge_policy({}, value)
        else:
            result[key] = value

    return result
