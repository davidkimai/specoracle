"""Policy dictionary merging utilities."""

_MISSING = object()


def _copy_value(value):
    """Copy dictionaries recursively while leaving non-dict values unchanged."""
    if isinstance(value, dict):
        return {key: _copy_value(item) for key, item in value.items()}
    return value


def _merge_dicts(defaults, override, allow_delete=True):
    """Merge two dictionaries according to policy override rules."""
    result = {key: _copy_value(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            if allow_delete:
                result.pop(key, None)
            continue

        current_value = result.get(key, _MISSING)

        if isinstance(current_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(current_value, override_value, allow_delete=allow_delete)
        elif isinstance(override_value, dict):
            result[key] = _merge_dicts({}, override_value, allow_delete=allow_delete)
        else:
            result[key] = override_value

    return result


def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    """
    Return a new policy dictionary created by applying override to defaults.

    Rules:
    - override values replace default values.
    - dictionaries are merged recursively when both sides have a dictionary.
    - an override value of None removes that key from the result when
      allow_delete is true.
    - an override value of None is ignored when allow_delete is false.
    - neither input dictionary is mutated.
    """
    return _merge_dicts(defaults, override, allow_delete=allow_delete)
