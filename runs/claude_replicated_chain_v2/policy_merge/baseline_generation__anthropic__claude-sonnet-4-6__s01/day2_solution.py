def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    result = {}
    all_keys = set(defaults) | set(override)
    for key in all_keys:
        if key in override:
            override_val = override[key]
            if override_val is None:
                if allow_delete:
                    continue
                else:
                    if key in defaults:
                        result[key] = defaults[key]
                    continue
            if key in defaults and isinstance(defaults[key], dict) and isinstance(override_val, dict):
                result[key] = merge_policy(defaults[key], override_val, allow_delete=allow_delete)
            else:
                result[key] = override_val
        else:
            result[key] = defaults[key]
    return result
