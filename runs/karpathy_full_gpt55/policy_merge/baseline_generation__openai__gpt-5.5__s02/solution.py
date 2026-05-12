def _copy_dict(value: dict) -> dict:
    """Return a recursive copy of dictionaries contained in *value*."""
    result = {}
    for key, item in value.items():
        result[key] = _copy_dict(item) if isinstance(item, dict) else item
    return result


def _merge(defaults: dict, override: dict) -> dict:
    result = _copy_dict(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
        elif isinstance(override_value, dict):
            current_value = result.get(key)
            if isinstance(current_value, dict):
                result[key] = _merge(current_value, override_value)
            else:
                result[key] = _merge({}, override_value)
        else:
            result[key] = override_value

    return result


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merge policy dictionaries without mutating either input.

    Override values take precedence. When both values for a key are dictionaries,
    they are merged recursively. An override value of None removes that key from
    the resulting dictionary.
    """
    return _merge(defaults, override)
