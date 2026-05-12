"""Policy dictionary merging."""

from __future__ import annotations

__all__ = ["merge_policy"]


_MISSING = object()


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge policy dictionaries without mutating either input.

    Values from ``override`` replace values from ``defaults``. When both values
    for a key are dictionaries, they are merged recursively. A ``None`` value in
    ``override`` deletes that key from the merged result.
    """
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dict")
    if not isinstance(override, dict):
        raise TypeError("override must be a dict")

    return _merge_dicts(defaults, override)


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = _copy_default_dict(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        current_value = result.get(key, _MISSING)
        if isinstance(current_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(current_value, override_value)
            continue

        result[key] = _copy_override_value(override_value)

    return result


def _copy_default_dict(source: dict) -> dict:
    return {key: _copy_default_value(value) for key, value in source.items()}


def _copy_default_value(value):
    if isinstance(value, dict):
        return _copy_default_dict(value)
    return value


def _copy_override_value(value):
    if isinstance(value, dict):
        return _merge_dicts({}, value)
    return value
