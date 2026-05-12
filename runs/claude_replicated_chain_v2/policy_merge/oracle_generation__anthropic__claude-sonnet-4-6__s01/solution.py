def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge two policy dictionaries.

    Override wins over defaults. Nested dicts are merged recursively.
    A None value in override removes the key from the result.
    Neither input is mutated.
    """
    result = {}

    all_keys = defaults.keys() | override.keys()

    for key in all_keys:
        if key in override:
            override_value = override[key]
            if override_value is None:
                continue
            default_value = defaults.get(key)
            if isinstance(override_value, dict) and isinstance(default_value, dict):
                result[key] = merge_policy(default_value, override_value)
            else:
                result[key] = override_value
        else:
            result[key] = defaults[key]

    return result
