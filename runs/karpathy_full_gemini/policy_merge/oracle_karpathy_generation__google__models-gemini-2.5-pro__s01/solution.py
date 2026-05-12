"""
A module for recursively merging dictionaries, representing policy configurations.
"""

from typing import Any, Dict


def merge_policy(defaults: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merges two dictionaries, `defaults` and `override`, into a new dictionary.

    The merge follows these rules:
    1. A new dictionary is always returned; inputs are not mutated.
    2. Keys from `override` take precedence over `defaults`.
    3. If a key exists in both dictionaries and both values are dictionaries,
       the values are merged recursively using the same rules.
    4. If a key in `override` has a value of `None`, that key is removed
       from the final merged dictionary.

    Args:
        defaults: The base dictionary.
        override: The dictionary with values to override the defaults.

    Returns:
        A new dictionary representing the merged result.
    """
    # Start with a shallow copy of the defaults to avoid mutating the original.
    merged = defaults.copy()

    for key, override_value in override.items():
        # If the override value is None, it acts as a signal to remove the key.
        if override_value is None:
            merged.pop(key, None)
            continue

        # Check if the key exists in the base and both values are dictionaries.
        # This is the condition for a recursive merge.
        if key in merged and isinstance(merged.get(key), dict) and isinstance(override_value, dict):
            merged[key] = merge_policy(merged[key], override_value)
        else:
            # Otherwise, the override value simply replaces the default value or
            # adds a new key-value pair.
            merged[key] = override_value

    return merged
