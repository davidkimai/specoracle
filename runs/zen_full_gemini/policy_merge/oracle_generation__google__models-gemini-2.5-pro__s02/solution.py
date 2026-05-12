"""
A module for deeply merging dictionary-based policies.
"""

from typing import Any, Dict


def merge_policy(defaults: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges two policy dictionaries, returning a new dictionary.

    The override dictionary wins over the defaults. If both values for a key
    are dictionaries, they are merged recursively. If the override value for a
    key is None, that key is removed from the result.

    This function does not mutate either of the input dictionaries.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary representing the merged policy.

    Raises:
        TypeError: If either input is not a dictionary.
    """
    if not isinstance(defaults, dict):
        raise TypeError("The 'defaults' argument must be a dictionary.")
    if not isinstance(override, dict):
        raise TypeError("The 'override' argument must be a dictionary.")

    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # A None value in the override acts as a deletion marker.
            merged.pop(key, None)
            continue

        default_value = merged.get(key)

        # Recursively merge if both the default and override values are dicts.
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            merged[key] = merge_policy(default_value, override_value)
        else:
            # Otherwise, the override value simply replaces the default.
            merged[key] = override_value

    return merged
