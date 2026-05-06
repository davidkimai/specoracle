from __future__ import annotations


def _require_dict(value: dict, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _copy_policy_value(value):
    if isinstance(value, dict):
        return {key: _copy_policy_value(item) for key, item in value.items()}
    return value


def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    _require_dict(defaults, "defaults")
    _require_dict(override, "override")

    result = {
        key: _copy_policy_value(value)
        for key, value in defaults.items()
    }

    for key, override_value in override.items():
        if override_value is None:
            if allow_delete:
                result.pop(key, None)
            continue

        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_policy(
                default_value,
                override_value,
                allow_delete=allow_delete,
            )
            continue

        result[key] = _copy_policy_value(override_value)

    return result
