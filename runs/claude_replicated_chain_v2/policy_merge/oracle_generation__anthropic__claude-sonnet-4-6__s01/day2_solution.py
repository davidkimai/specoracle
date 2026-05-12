def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    """Merge two policy dictionaries.

    Override wins over defaults. Nested dicts are merged recursively.
    A None value in override removes the key from the result when
    allow_delete is True (the default). When allow_delete is False,
    None values in override are ignored and the default value (if any)
    is kept.
    Neither input is mutated.
    """
    result = {}

    all_keys = defaults.keys() | override.keys()

    for key in all_keys:
        if key in override:
            override_value = override[key]
            if override_value is None:
                if allow_delete:
                    continue
                else:
                    # Ignore the None; fall back to default if present
                    if key in defaults:
                        result[key] = defaults[key]
                    continue
            default_value = defaults.get(key)
            if isinstance(override_value, dict) and isinstance(default_value, dict):
                result[key] = merge_policy(default_value, override_value, allow_delete=allow_delete)
            else:
                result[key] = override_value
        else:
            result[key] = defaults[key]

    return result
