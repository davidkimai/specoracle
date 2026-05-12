import collections.abc

def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merges two dictionaries representing policies.

    The merge logic is as follows:
    1. Returns a new dictionary, leaving the original inputs unmodified.
    2. Keys from `override` take precedence over keys from `defaults`.
    3. If a key exists in both dictionaries and both values are dictionaries,
       the values are merged recursively.
    4. If a key in `override` has a value of `None`, that key is removed
       from the final merged dictionary.

    Args:
        defaults: The base dictionary.
        override: The dictionary with overriding values.

    Returns:
        A new dictionary representing the merged policy.
    """
    # Start with a copy of the defaults to avoid mutating the original
    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # If the override value is None, remove the key from the merged dict.
            merged.pop(key, None)
            continue

        default_value = merged.get(key)

        # Check for recursive merge condition: both values must be dict-like.
        if (isinstance(default_value, collections.abc.Mapping) and
                isinstance(override_value, collections.abc.Mapping)):
            merged[key] = merge_policy(default_value, override_value)
        else:
            # Otherwise, the override value simply replaces the default.
            merged[key] = override_value

    return merged
