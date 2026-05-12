_MISSING = object()


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merge two policy dictionaries without mutating either input.

    Rules:
    - Values from override take precedence over defaults.
    - If both values for a key are dictionaries, they are merged recursively.
    - If override contains a key with value None, that key is removed from the
      resulting dictionary.
    """
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dict")
    if not isinstance(override, dict):
        raise TypeError("override must be a dict")

    return _merge_dicts(defaults, override)


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = _copy_default_dict(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = defaults.get(key, _MISSING)

        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(default_value, override_value)
        else:
            result[key] = _copy_override_value(override_value)

    return result


def _copy_default_dict(value: dict) -> dict:
    return {key: _copy_default_value(item) for key, item in value.items()}


def _copy_default_value(value):
    if isinstance(value, dict):
        return _copy_default_dict(value)
    if isinstance(value, list):
        return [_copy_default_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_copy_default_value(item) for item in value)
    if isinstance(value, set):
        return {_copy_default_value(item) for item in value}
    if isinstance(value, frozenset):
        return frozenset(_copy_default_value(item) for item in value)
    return value


def _copy_override_dict(value: dict) -> dict:
    result = {}

    for key, item in value.items():
        if item is None:
            continue
        result[key] = _copy_override_value(item)

    return result


def _copy_override_value(value):
    if isinstance(value, dict):
        return _copy_override_dict(value)
    if isinstance(value, list):
        return [_copy_override_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_copy_override_value(item) for item in value)
    if isinstance(value, set):
        return {_copy_override_value(item) for item in value}
    if isinstance(value, frozenset):
        return frozenset(_copy_override_value(item) for item in value)
    return value
