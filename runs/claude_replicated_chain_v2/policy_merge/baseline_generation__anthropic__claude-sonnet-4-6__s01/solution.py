def merge_policy(defaults: dict, override: dict) -> dict:
    result = {}
    all_keys = set(defaults) | set(override)
    for key in all_keys:
        if key in override:
            override_val = override[key]
            if override_val is None:
                continue
            if key in defaults and isinstance(defaults[key], dict) and isinstance(override_val, dict):
                result[key] = merge_policy(defaults[key], override_val)
            else:
                result[key] = override_val
        else:
            result[key] = defaults[key]
    return result
