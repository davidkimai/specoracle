"""
A module for flattening nested dictionaries.
"""

from typing import Any, Dict


def flatten_paths(value: dict) -> dict[str, object]:
    """
    Flattens a nested dictionary into a single-level dictionary with dot-path keys.

    Lists and other non-dict values are treated as leaf nodes and are not traversed.
    Empty dictionaries are also treated as leaf nodes.

    For example:
        >>> flatten_paths({'a': {'b': 1, 'c': [2, 3]}, 'd': 4})
        {'a.b': 1, 'a.c': [2, 3], 'd': 4}

    Args:
        value: The nested dictionary to flatten.

    Returns:
        A new dictionary with flattened keys.
    """
    result: Dict[str, object] = {}

    def _traverse(current_dict: Dict[str, Any], parent_key: str):
        """
        Recursively traverses the dictionary, building up flattened keys.
        """
        for key, val in current_dict.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(val, dict) and val:
                _traverse(val, new_key)
            else:
                result[new_key] = val

    _traverse(value, '')
    return result
