"""
A module for recursively merging dictionaries representing policies.
"""

from typing import Any, Dict


def merge_policy(defaults: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merges two dictionaries, `defaults` and `override`, into a new dictionary.

    The merging logic is as follows:
    - A new dictionary is created, starting with a copy of `defaults`.
    - Keys and values from `override` are then applied.
    - If a key exists in both, the value from `override` is used.
    - If the values for a key in both dictionaries are themselves dictionaries,
      they are merged recursively using the same logic.
    - If a value in `override` is `None`, the corresponding key is removed
      from the merged dictionary.
    - The original `defaults` and `override` dictionaries are not modified.

    Args:
        defaults: The base dictionary.
        override: The dictionary with values to override the defaults.

    Returns:
        A new dictionary representing the merged policy.
    """
    # Start with a copy of defaults to ensure the original is not mutated.
    result = defaults.copy()

    for key, override_value in override.items():
        # If the override value is None, the key should be removed from the result.
        if override_value is None:
            result.pop(key, None)
        # If the key exists in the base and both values are dictionaries,
        # merge them recursively.
        elif (key in result and
              isinstance(result[key], dict) and
              isinstance(override_value, dict)):
            result[key] = merge_policy(result[key], override_value)
        # Otherwise, the override value simply replaces the default value or is added.
        else:
            result[key] = override_value

    return result
