"""
A module for securely merging policy dictionaries.
"""

from typing import Dict, Any, TypeVar

# Use a TypeVar to represent the dictionary type for more precise typing if needed,
# but for this generic function, Dict[str, Any] is sufficient and clear.
D = TypeVar('D', bound=Dict[str, Any])


def merge_policy(defaults: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges two dictionaries, giving precedence to the override dictionary.

    This function creates a new dictionary by merging 'defaults' and 'override'.
    The merge logic is as follows:
    - The operation is non-mutating; it returns a new dictionary and does not
      modify the input dictionaries.
    - Keys from 'override' will overwrite keys from 'defaults'.
    - If a key exists in both dictionaries and both corresponding values are
      dictionaries, the function will recursively merge the nested dictionaries.
    - If a key in 'override' has a value of None, that key will be removed
      from the final merged dictionary.

    Args:
        defaults: The base dictionary with default values.
        override: The dictionary with override values.

    Returns:
        A new dictionary representing the merged policy.
    """
    # Start with a copy of the defaults to avoid mutating the original.
    merged = defaults.copy()

    for key, override_value in override.items():
        if override_value is None:
            # If the override value is None, remove the key from the result.
            # The second argument to pop ensures no KeyError is raised if the
            # key was not in the defaults dictionary to begin with.
            merged.pop(key, None)
        elif (key in merged and
              isinstance(merged[key], dict) and
              isinstance(override_value, dict)):
            # If the key exists in both and both values are dictionaries,
            # merge them recursively.
            merged[key] = merge_policy(merged[key], override_value)
        else:
            # Otherwise, the override value (which is not None) takes precedence,
            # either by overwriting the existing key or adding a new one.
            merged[key] = override_value

    return merged
