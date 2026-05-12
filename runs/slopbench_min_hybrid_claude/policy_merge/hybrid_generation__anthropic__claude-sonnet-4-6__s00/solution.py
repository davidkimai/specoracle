def _both_dicts(a, b):
    return isinstance(a, dict) and isinstance(b, dict)


def _merge_key(key, defaults, override):
    """Return (include, value) for a single key during merge."""
    in_defaults = key in defaults
    in_override = key in override

    override_value = override.get(key)
    default_value = defaults.get(key)

    if in_override and override_value is None:
        return False, None

    if in_defaults and in_override and _both_dicts(default_value, override_value):
        return True, merge_policy(default_value, override_value)

    if in_override:
        return True, override_value

    return True, default_value


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge two policy dicts; override wins, None removes, dicts recurse."""
    all_keys = set(defaults) | set(override)
    result = {}
    for key in all_keys:
        include, value = _merge_key(key, defaults, override)
        if include:
            result[key] = value
    return result
