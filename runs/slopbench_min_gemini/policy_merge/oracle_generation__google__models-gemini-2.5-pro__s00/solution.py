import collections.abc


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merges two dictionaries, `defaults` and `override`, into a new dictionary.

    The merge logic is as follows:
    1. Keys from `override` take precedence over `defaults`.
    2. If a key exists in both and the values are both dictionaries, the
       dictionaries are merged recursively.
    3. If a key in `override` has a value of `None`, that key is removed
       from the final merged dictionary.
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
        raise TypeError(
            f"Expected 'defaults' to be a dictionary, "
            f"but got {type(defaults).__name__}"
        )
    if not isinstance(override, dict):
        raise TypeError(
            f"Expected 'override' to be a dictionary, "
            f"but got {type(override).__name__}"
        )

    merged = defaults.copy()

    for key, value in override.items():
        if value is None:
            # If the override value is None, remove the key from the result.
            merged.pop(key, None)
            continue

        is_dict_in_merged = key in merged and isinstance(merged[key], dict)
        is_dict_in_override = isinstance(value, dict)

        if is_dict_in_merged and is_dict_in_override:
            # If both values are dicts, merge them recursively.
            merged[key] = merge_policy(merged[key], value)
        else:
            # Otherwise, the override value wins completely.
            merged[key] = value

    return merged
