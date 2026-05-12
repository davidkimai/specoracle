def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merge policy dictionaries without mutating either input.

    Override values replace default values. If both values for a key are
    dictionaries, they are merged recursively. An override value of None removes
    the key from the result.
    """
    result = {key: _copy_dicts(value) for key, value in defaults.items()}

    for key, value in override.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_policy(result[key], value)
        else:
            result[key] = _copy_dicts(value)

    return result


def _copy_dicts(value):
    if isinstance(value, dict):
        return {key: _copy_dicts(child) for key, child in value.items()}
    return value
