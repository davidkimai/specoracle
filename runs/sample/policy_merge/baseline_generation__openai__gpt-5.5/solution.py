"""Policy dictionary merging utilities."""

_MISSING = object()


def _copy_value(value):
    """Copy dictionaries recursively while leaving non-dict values unchanged."""
    if isinstance(value, dict):
        return {key: _copy_value(item) for key, item in value.items()}
    return value


def _merge_dicts(defaults, override):
    """Merge two dictionaries according to policy override rules."""
    result = {key: _copy_value(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        current_value = result.get(key, _MISSING)

        if isinstance(current_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(current_value, override_value)
        elif isinstance(override_value, dict):
            result[key] = _merge_dicts({}, override_value)
        else:
            result[key] = override_value

    return result


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Return a new policy dictionary created by applying override to defaults.

    Rules:
    - override values replace default values.
    - dictionaries are merged recursively when both sides have a dictionary.
    - an override value of None removes that key from the result.
    - neither input dictionary is mutated.
    """
    return _merge_dicts(defaults, override)
