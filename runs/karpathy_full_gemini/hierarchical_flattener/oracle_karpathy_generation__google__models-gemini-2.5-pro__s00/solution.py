"""
A module for flattening nested dictionaries into dot-path keys.
"""

from typing import Any, Dict


def flatten_paths(value: Dict[Any, Any]) -> Dict[str, Any]:
    """Flattens a nested dictionary into a single-level dictionary.

    The keys of the returned dictionary are dot-separated paths that represent
    the path to the values in the original nested structure.

    Lists and empty dictionaries are treated as leaf values and are not
    traversed further.

    Example:
        >>> data = {'a': {'b': 1, 'c': [2, 3]}, 'd': {}}
        >>> flatten_paths(data)
        {'a.b': 1, 'a.c': [2, 3], 'd': {}}

    Args:
        value: The nested dictionary to flatten.

    Returns:
        A dictionary with flattened, dot-separated keys.

    Raises:
        TypeError: If the input value is not a dictionary.
    """
    if not isinstance(value, dict):
        raise TypeError("Input must be a dictionary.")

    flat_dict: Dict[str, Any] = {}

    def _traverse(obj: Any, path: str) -> None:
        """Recursively traverses the object to build the flattened dictionary."""
        if isinstance(obj, dict) and obj:
            for key, val in obj.items():
                new_path = f"{path}.{key}" if path else str(key)
                _traverse(val, new_path)
        elif path:
            # A non-empty path indicates this is not the top-level empty dict.
            flat_dict[path] = obj

    _traverse(value, "")
    return flat_dict
