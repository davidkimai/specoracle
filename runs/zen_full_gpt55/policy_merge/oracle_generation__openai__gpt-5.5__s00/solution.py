def _require_dict(value: object, name: str) -> dict:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")
    return value


def _copy_default_value(value: object) -> object:
    if isinstance(value, dict):
        return {key: _copy_default_value(item) for key, item in value.items()}
    return value


def _copy_override_dict(value: dict) -> dict:
    result = {}

    for key, item in value.items():
        if item is None:
            continue
        if isinstance(item, dict):
            result[key] = _copy_override_dict(item)
        else:
            result[key] = item

    return result


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = {key: _copy_default_value(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = defaults.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(default_value, override_value)
            continue

        if isinstance(override_value, dict):
            result[key] = _copy_override_dict(override_value)
            continue

        result[key] = override_value

    return result


def merge_policy(defaults: dict, override: dict) -> dict:
    defaults = _require_dict(defaults, "defaults")
    override = _require_dict(override, "override")
    return _merge_dicts(defaults, override)
