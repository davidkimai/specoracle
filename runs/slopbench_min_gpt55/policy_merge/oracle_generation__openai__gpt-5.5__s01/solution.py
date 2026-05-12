"""Policy dictionary merging utilities."""


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge two policy dictionaries without mutating either input.

    Values from ``override`` win over values from ``defaults``. When both values
    for a key are dictionaries, they are merged recursively. A key in
    ``override`` with value ``None`` removes that key from the result.
    """
    _require_dict(defaults, "defaults")
    _require_dict(override, "override")
    return _merge_dicts(defaults, override)


def _require_dict(value: object, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = {key: _copy_dict_values(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        current_value = result.get(key)
        if isinstance(current_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(current_value, override_value)
            continue

        result[key] = _copy_dict_values(override_value)

    return result


def _copy_dict_values(value: object) -> object:
    if not isinstance(value, dict):
        return value

    return {key: _copy_dict_values(child_value) for key, child_value in value.items()}
