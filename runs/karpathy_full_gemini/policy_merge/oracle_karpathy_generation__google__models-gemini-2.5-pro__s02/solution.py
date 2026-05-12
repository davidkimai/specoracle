"""
A module for merging policy dictionaries.
"""

import typing


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merges two dictionaries, 'defaults' and 'override', into a new dictionary.

    The merging rules are as follows:
    1. A new dictionary is always returned; the input dictionaries are not mutated.
    2. Keys from 'override' take precedence over 'defaults'.
    3. If a key exists in both dictionaries and both corresponding values are
       dictionaries, the two dictionaries are recursively merged.
    4. If a key in 'override' has a value of None, that key is removed from the
       final merged dictionary, even if it exists in 'defaults'.

    Args:
        defaults: The base dictionary.
        override: The dictionary with values to override the defaults.

    Returns:
        A new dictionary representing the merged policy.
    """
    # Start with a shallow copy of defaults to avoid mutating the original.
    # Any nested dictionaries will be handled by the recursive calls, which
    # will in turn create their own copies, ensuring non-mutation.
    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # If the override value is None, remove the key from the result.
            if key in merged:
                del merged[key]
        elif key in merged and isinstance(merged[key], dict) and \
                isinstance(override_value, dict):
            # If the key exists in both and both values are dictionaries,
            # recursively merge them.
            merged[key] = merge_policy(merged[key], override_value)
        else:
            # Otherwise, the override value (which is not None) simply
            # replaces the old value or adds a new key-value pair.
            merged[key] = override_value

    return merged
