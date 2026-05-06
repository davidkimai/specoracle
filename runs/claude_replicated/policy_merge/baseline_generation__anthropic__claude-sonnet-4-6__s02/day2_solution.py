def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    result = {}

    for key, value in defaults.items():
        if key in override:
            override_value = override[key]
            if override_value is None:
                if not allow_delete:
                    result[key] = value
                # else: omit key (delete it)
            elif isinstance(value, dict) and isinstance(override_value, dict):
                result[key] = merge_policy(value, override_value, allow_delete=allow_delete)
            else:
                result[key] = override_value
        else:
            result[key] = value

    for key, value in override.items():
        if key not in defaults:
            if value is not None:
                result[key] = value

    return result
