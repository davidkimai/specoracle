"""
A module for flattening hierarchical data structures.
"""

from typing import Any, Dict


def _build_path(parent_path: str, key: Any) -> str:
    """
    Builds a dot-separated path, converting the key to a string.

    Args:
        parent_path: The existing path prefix.
        key: The new key to append to the path.

    Returns:
        The newly constructed path string.
    """
    key_str = str(key)
    if not parent_path:
        return key_str
    return f"{parent_path}.{key_str}"


def _flatten_recursively(
    data: Dict[Any, Any], parent_path: str
) -> Dict[str, object]:
    """
    Recursively flattens a dictionary helper function.

    Args:
        data: The dictionary to flatten.
        parent_path: The prefix to prepend to keys discovered in `data`.

    Returns:
        A new dictionary with flattened keys.
    """
    flattened: Dict[str, object] = {}
    for key, value in data.items():
        current_path = _build_path(parent_path, key)
        if isinstance(value, dict) and value:
            # Recurse into non-empty dictionaries.
            flattened.update(_flatten_recursively(value, current_path))
        else:
            # Treat non-dict values, lists, and empty dicts as leaves.
            flattened[current_path] = value
    return flattened


def flatten_paths(value: dict) -> Dict[str, object]:
    """
    Flattens a nested dictionary into a single level with dot-separated keys.

    Lists and empty dictionaries are treated as leaf values and are not traversed.
    Keys are converted to strings to form the dot-separated path.

    Example:
        >>> data = {'a': 1, 'b': {'c': 2, 'd': {}}, 'e': [4, 5]}
        >>> flatten_paths(data)
        {'a': 1, 'b.c': 2, 'b.d': {}, 'e': [4, 5]}

    Args:
        value: The dictionary to flatten.

    Returns:
        A new dictionary with flattened keys and their corresponding values.

    Raises:
        TypeError: If the input `value` is not a dictionary.
    """
    if not isinstance(value, dict):
        raise TypeError("Input must be a dictionary.")

    return _flatten_recursively(value, "")
