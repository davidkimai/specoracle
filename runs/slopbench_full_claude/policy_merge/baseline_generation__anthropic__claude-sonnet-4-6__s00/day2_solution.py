def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    result = {}
    all_keys = set(defaults) | set(override)
    for key in all_keys:
        if key in override:
            if override[key] is None:
                if allow_delete:
                    continue
                else:
                    if key in defaults:
                        result[key] = defaults[key]
                    continue
            if key in defaults and isinstance(defaults[key], dict) and isinstance(override[key], dict):
                result[key] = merge_policy(defaults[key], override[key], allow_delete=allow_delete)
            else:
                result[key] = override[key]
        else:
            result[key] = defaults[key]
    return result
