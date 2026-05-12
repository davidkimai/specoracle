"""A module for recursively merging dictionary-based policies."""

from typing import Any, Dict


def merge_policy(defaults: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merges two dictionaries recursively to produce a new policy dictionary.

    The merge logic is as follows:
    - A new dictionary is created; the input dictionaries are not mutated.
    - For keys present in both `defaults` and `override`:
        - If both corresponding values are dictionaries, they are merged
          recursively.
        - Otherwise, the value from `override` is used.
    - For keys present only in `override`:
        - If the value is `None`, the key is omitted from the result.
        - Otherwise, the key-value pair is added to the result.
    - Keys present only in `defaults` are retained.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary representing the merged policy.

    Raises:
        TypeError: If either `defaults` or `override` is not a dictionary.
    """
    if not isinstance(defaults, dict):
        raise TypeError(
            f"defaults must be a dictionary, but got {type(defaults).__name__}"
        )
    if not isinstance(override, dict):
        raise TypeError(
            f"override must be a dictionary, but got {type(override).__name__}"
        )

    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # A None value in the override acts as a tombstone, removing the key.
            merged.pop(key, None)
            continue

        default_value = merged.get(key)

        is_recursive_merge = (
            isinstance(default_value, dict) and isinstance(override_value, dict)
        )

        if is_recursive_merge:
            # If both values are dictionaries, merge them recursively.
            merged[key] = merge_policy(default_value, override_value)
        else:
            # Otherwise, the override value replaces the default.
            merged[key] = override_value

    return merged
