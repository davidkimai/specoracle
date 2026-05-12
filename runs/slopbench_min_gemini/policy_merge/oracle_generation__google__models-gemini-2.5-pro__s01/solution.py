"""
A module for recursively merging dictionary-based policies.
"""


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merges two dictionaries, producing a new dictionary with specific rules.

    The merge logic is as follows:
    1. The 'override' dictionary's values take precedence over 'defaults'.
    2. If a key exists in both dictionaries and both corresponding values are
       dictionaries, they are merged recursively using the same policy.
    3. If a key in the 'override' dictionary has a value of None, that key is
       removed from the final merged dictionary.
    4. The input dictionaries are not mutated.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary representing the merged policy.

    Raises:
        TypeError: If either 'defaults' or 'override' is not a dictionary.
    """
    if not isinstance(defaults, dict):
        raise TypeError("The 'defaults' argument must be a dictionary.")
    if not isinstance(override, dict):
        raise TypeError("The 'override' argument must be a dictionary.")

    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            merged.pop(key, None)
            continue

        default_value = merged.get(key)

        is_recursive_merge = (
            isinstance(default_value, dict) and
            isinstance(override_value, dict)
        )

        if is_recursive_merge:
            merged[key] = merge_policy(default_value, override_value)
        else:
            merged[key] = override_value

    return merged
