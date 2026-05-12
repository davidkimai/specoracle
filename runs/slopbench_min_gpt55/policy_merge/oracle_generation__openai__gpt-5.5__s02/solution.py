"""Policy dictionary merging utilities."""


def _require_dict(name: str, value: dict) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _copy_dict(value: dict) -> dict:
    return {
        key: _copy_dict(item) if isinstance(item, dict) else item
        for key, item in value.items()
    }


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = _copy_dict(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        current_value = result.get(key)
        if isinstance(current_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(current_value, override_value)
            continue

        if isinstance(override_value, dict):
            result[key] = _copy_dict(override_value)
            continue

        result[key] = override_value

    return result


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge policy dictionaries without mutating either input."""
    _require_dict("defaults", defaults)
    _require_dict("override", override)
    return _merge_dicts(defaults, override)
