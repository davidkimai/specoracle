def merge_policy(defaults: dict, override: dict) -> dict:
    result = {}
    all_keys = set(defaults) | set(override)
    for key in all_keys:
        if key in override:
            if override[key] is None:
                continue
            if key in defaults and isinstance(defaults[key], dict) and isinstance(override[key], dict):
                result[key] = merge_policy(defaults[key], override[key])
            else:
                result[key] = override[key]
        else:
            result[key] = defaults[key]
    return result
