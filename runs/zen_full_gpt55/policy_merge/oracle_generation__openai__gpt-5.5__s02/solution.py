"""Policy dictionary merging utilities."""

from collections.abc import Mapping


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge two policy dictionaries without mutating either input.

    Values from ``override`` take precedence over values from ``defaults``.
    Nested dictionaries are merged recursively. A key set to ``None`` in
    ``override`` removes that key from the returned dictionary.
    """
    _require_dict(defaults, "defaults")
    _require_dict(override, "override")
    return _merge_dicts(defaults, override)


def _require_dict(value: object, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _merge_dicts(defaults: Mapping, override: Mapping) -> dict:
    result = {key: _copy_dicts(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(default_value, override_value)
            continue

        result[key] = _copy_dicts(override_value)

    return result


def _copy_dicts(value: object) -> object:
    if not isinstance(value, dict):
        return value

    return {key: _copy_dicts(nested_value) for key, nested_value in value.items()}
