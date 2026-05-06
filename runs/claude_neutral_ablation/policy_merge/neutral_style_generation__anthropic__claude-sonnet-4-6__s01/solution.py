def merge_policy(defaults: dict, override: dict) -> dict:
    result = {}

    for key, default_value in defaults.items():
        if key in override:
            override_value = override[key]
            if override_value is None:
                pass  # Remove the key from result
            elif isinstance(default_value, dict) and isinstance(override_value, dict):
                result[key] = merge_policy(default_value, override_value)
            else:
                result[key] = override_value
        else:
            result[key] = default_value

    for key, override_value in override.items():
        if key not in defaults:
            if override_value is not None:
                result[key] = override_value

    return result
