"""
A module for merging policy dictionaries.
"""

import collections.abc
from typing import Dict, Any


def merge_policy(defaults: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merges two dictionaries representing policies, producing a new dictionary.

    The merge logic is as follows:
    1. A new dictionary is created, starting with a copy of `defaults`.
    2. Keys from `override` are merged into the new dictionary.
    3. If a key exists in both, the value from `override` is used.
    4. If a value in `override` is None, the key is removed from the result.
    5. If a key exists in both and both values are dictionaries, they are
       merged recursively.
    6. The original input dictionaries are not mutated.

    Args:
        defaults: The base dictionary.
        override: The dictionary with override values.

    Returns:
        A new dictionary with the merged policies.
    """
    # Start with a shallow copy of the defaults to avoid mutating the original.
    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # If the override value is None, remove the key from the merged dict.
            merged.pop(key, None)
        elif key in merged and isinstance(merged.get(key), dict) and isinstance(
            override_value, collections.abc.Mapping
        ):
            # If both values are dictionaries, merge them recursively.
            # We check override_value against Mapping for more flexibility and
            # merged.get(key) against dict to match the recursive call's type hint.
            merged[key] = merge_policy(merged[key], dict(override_value))
        else:
            # Otherwise, the override value simply replaces the default value.
            merged[key] = override_value

    return merged
