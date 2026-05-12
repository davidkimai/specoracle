"""Policy merging utilities."""

from typing import Any


def _copy_value(value: Any) -> Any:
    """Recursively copy dictionaries while leaving non-dict values unchanged."""
    if isinstance(value, dict):
        return {key: _copy_value(child) for key, child in value.items()}
    return value


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merge two policy dictionaries without mutating either input.

    Rules:
    - Values from ``override`` take precedence over values from ``defaults``.
    - If both values for a key are dictionaries, they are merged recursively.
    - If ``override`` contains a key with value ``None``, that key is removed
      from the result.
    """
    result = _copy_value(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_policy(default_value, override_value)
        else:
            result[key] = _copy_value(override_value)

    return result
