def _both_dicts(a, b):
    return isinstance(a, dict) and isinstance(b, dict)


def _merge_key(default_value, override_value):
    if _both_dicts(default_value, override_value):
        return merge_policy(default_value, override_value)
    return override_value


def _apply_defaults(defaults, override, result):
    for key, default_value in defaults.items():
        override_value = override.get(key, default_value)
        if override_value is None:
            continue
        result[key] = _merge_key(default_value, override_value) if key in override else default_value


def _apply_overrides(defaults, override, result):
    for key, override_value in override.items():
        if key in defaults or override_value is None:
            continue
        result[key] = override_value


def merge_policy(defaults: dict, override: dict) -> dict:
    result = {}
    _apply_defaults(defaults, override, result)
    _apply_overrides(defaults, override, result)
    return result
