"""Policy merging utilities."""

from typing import Any


def _clone_dict_containers(value: Any) -> Any:
    """Recursively clone dictionary containers, leaving non-dict values as-is."""
    if isinstance(value, dict):
        return {key: _clone_dict_containers(item) for key, item in value.items()}
    return value


def _merge_dicts(defaults: dict, override: dict) -> dict:
    """Merge two dictionaries according to policy-merge semantics."""
    result = _clone_dict_containers(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(default_value, override_value)
        else:
            result[key] = _clone_dict_containers(override_value)

    return result


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Return a merged policy dictionary.

    The override dictionary wins over defaults. If both values for a key are
    dictionaries, they are merged recursively. If override contains a key with
    value None, that key is removed from the result. Neither input dictionary is
    mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dict")
    if not isinstance(override, dict):
        raise TypeError("override must be a dict")

    return _merge_dicts(defaults, override)
