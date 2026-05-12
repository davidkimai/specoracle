def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge policy dictionaries without mutating either input.

    Override values replace defaults. When both values are dictionaries, they are
    merged recursively. A key present in override with value None is removed from
    the result.
    """
    result = _copy_defaults(defaults)

    for key, value in override.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict):
            if isinstance(result.get(key), dict):
                result[key] = merge_policy(result[key], value)
            else:
                result[key] = merge_policy({}, value)
        else:
            result[key] = value

    return result


def _copy_defaults(value: dict) -> dict:
    result = {}
    for key, item in value.items():
        if isinstance(item, dict):
            result[key] = _copy_defaults(item)
        else:
            result[key] = item
    return result
