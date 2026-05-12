"""
A module for flattening hierarchical data structures.
"""

from typing import Any, Dict


def flatten_paths(value: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens a nested dictionary into a single-level dictionary.

    Nested keys are combined into a single key using dot notation. Lists
    and other non-dict values (including empty dicts) are treated as leaves
    and are not traversed.

    Args:
        value: The dictionary to flatten.

    Returns:
        A new dictionary with flattened keys.

    Raises:
        TypeError: If the input is not a dictionary or if any of the keys
                   in the nested dictionaries are not strings.

    Example:
        >>> data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}, 'f': [4, 5]}
        >>> flatten_paths(data)
        {'a': 1, 'b.c': 2, 'b.d.e': 3, 'f': [4, 5]}
    """
    if not isinstance(value, dict):
        raise TypeError("Input must be a dictionary.")

    flattened_dict: Dict[str, Any] = {}
    _flatten_recursive(value, "", flattened_dict)
    return flattened_dict


def _flatten_recursive(
    current_dict: Dict[str, Any],
    parent_path: str,
    result: Dict[str, Any]
) -> None:
    """
    Recursively flattens a dictionary.

    Args:
        current_dict: The current dictionary to process.
        parent_path: The path of keys leading to the current value.
        result: The dictionary to which flattened key-value pairs are added.
    """
    for key, val in current_dict.items():
        if not isinstance(key, str):
            raise TypeError(
                f"Dictionary keys must be strings to be flattened, but got key "
                f"'{key}' of type {type(key).__name__} at path '{parent_path}'."
            )

        new_path = f"{parent_path}.{key}" if parent_path else key

        # Recurse only if the value is a non-empty dictionary.
        # Empty dictionaries and other types (lists, etc.) are treated as leaves.
        if isinstance(val, dict) and val:
            _flatten_recursive(val, new_path, result)
        else:
            result[new_path] = val
