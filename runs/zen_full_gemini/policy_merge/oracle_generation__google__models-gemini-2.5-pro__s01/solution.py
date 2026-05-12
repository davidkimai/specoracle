"""
Provides a function for recursively merging dictionary-based policies.
"""

def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merges two dictionaries, returning a new dictionary.

    The merge strategy is as follows:
    1. The override dictionary's values take precedence over the defaults.
    2. If a value for a key is a dictionary in both `defaults` and
       `override`, the dictionaries are merged recursively.
    3. If a key in `override` has a value of `None`, that key is
       removed from the final merged dictionary.
    4. The original input dictionaries are not mutated.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary representing the merged policy.

    Raises:
        TypeError: If either `defaults` or `override` is not a dictionary.
    """
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dictionary")
    if not isinstance(override, dict):
        raise TypeError("override must be a dictionary")

    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            merged.pop(key, None)
            continue

        default_value = merged.get(key)

        if isinstance(default_value, dict) and isinstance(override_value, dict):
            merged[key] = merge_policy(default_value, override_value)
        else:
            merged[key] = override_value

    return merged
