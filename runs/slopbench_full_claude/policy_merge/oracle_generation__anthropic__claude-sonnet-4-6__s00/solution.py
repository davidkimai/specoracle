def merge_policy(defaults: dict, override: dict) -> dict:
    result = {}

    for key, default_value in defaults.items():
        if key not in override:
            result[key] = default_value
            continue

        override_value = override[key]

        if override_value is None:
            continue

        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_policy(default_value, override_value)
        else:
            result[key] = override_value

    for key, override_value in override.items():
        if key in defaults:
            continue
        if override_value is None:
            continue
        result[key] = override_value

    return result
