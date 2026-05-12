"""A module for merging policy dictionaries."""

from typing import Any, Dict


def merge_policy(defaults: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges two policy dictionaries, returning a new dictionary.

    The merge logic is as follows:
    - The override dictionary wins over the defaults.
    - If both values for a key are dictionaries, they are merged recursively.
    - If a key in the override dictionary has a value of None, that key is
      removed from the result.
    - The input dictionaries are not mutated.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary representing the merged policy.
    """
    # Start with a copy of defaults to ensure the original is not mutated.
    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # If the override value is None, remove the key from the merged dict.
            merged.pop(key, None)
        elif (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(override_value, dict)
        ):
            # If both values are dictionaries, merge them recursively.
            merged[key] = merge_policy(merged[key], override_value)
        else:
            # Otherwise, the override value replaces the default value.
            merged[key] = override_value

    return merged
