"""
A module for merging dictionary-based policies.
"""


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merges two dictionary-based policies, with override taking precedence.

    This function creates a new dictionary representing the merged policy.
    It does not mutate the input dictionaries.

    The merging rules are as follows:
    1. Keys and values from `defaults` are copied to the result.
    2. For each key in `override`:
       - If the value is None, the key is removed from the result.
       - If the key exists in both dictionaries and both values are
         dictionaries, the two dictionaries are merged recursively.
       - Otherwise, the value from `override` replaces the value in the result.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary containing the merged policy.

    Raises:
        TypeError: If either `defaults` or `override` is not a dictionary.
    """
    if not isinstance(defaults, dict):
        raise TypeError("The 'defaults' argument must be a dictionary.")
    if not isinstance(override, dict):
        raise TypeError("The 'override' argument must be a dictionary.")

    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # If the override value is None, ensure the key is removed.
            merged.pop(key, None)
            continue

        default_value = merged.get(key)

        is_recursive_merge = (
            isinstance(default_value, dict) and
            isinstance(override_value, dict)
        )

        if is_recursive_merge:
            # Both values are dictionaries, so merge them recursively.
            merged[key] = merge_policy(default_value, override_value)
        else:
            # Otherwise, the override value simply replaces the default.
            merged[key] = override_value

    return merged
