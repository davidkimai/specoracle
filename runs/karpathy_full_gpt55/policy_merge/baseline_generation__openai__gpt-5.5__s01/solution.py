"""Policy dictionary merging utilities."""

from copy import deepcopy
from typing import Any

__all__ = ["merge_policy"]


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge policy dictionaries without mutating either input.

    Values from ``override`` take precedence over values from ``defaults``.
    When both corresponding values are dictionaries, they are merged
    recursively. A key present in ``override`` with value ``None`` is deleted
    from the merged result.
    """
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dict")
    if not isinstance(override, dict):
        raise TypeError("override must be a dict")

    return _merge_dicts(defaults, override)


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = {key: _clone_value(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        existing_value = result.get(key)

        if isinstance(existing_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(existing_value, override_value)
        elif isinstance(override_value, dict):
            result[key] = _merge_dicts({}, override_value)
        else:
            result[key] = deepcopy(override_value)

    return result


def _clone_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _merge_dicts(value, {})
    return deepcopy(value)
