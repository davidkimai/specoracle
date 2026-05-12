"""A module for flattening nested dictionaries."""

from typing import Any


def flatten_paths(value: dict) -> dict[str, object]:
    """Flattens a nested dictionary into a single-level dictionary.

    The keys of the new dictionary are dot-separated paths representing the
    nested structure of the original dictionary. Keys in the path are
    converted to strings.

    Lists and other non-dict values are treated as leaf values and are not
    recursed into.

    Args:
        value: The nested dictionary to flatten.

    Returns:
        A new dictionary with flattened key-value pairs.

    Example:
        >>> flatten_paths({'a': 1, 'b': {'c': 2, 'd': [3, 4]}})
        {'a': 1, 'b.c': 2, 'b.d': [3, 4]}
        >>> flatten_paths({1: {'two': 3}})
        {'1.two': 3}
    """
    if not isinstance(value, dict):
        raise TypeError("Input must be a dictionary.")

    flattened_dict: dict[str, object] = {}

    def _traverse(sub_value: Any, path: str) -> None:
        """Recursively traverses the dictionary to build flattened paths."""
        if isinstance(sub_value, dict):
            for key, val in sub_value.items():
                new_path = f"{path}.{key}" if path else str(key)
                _traverse(val, new_path)
        else:
            # Reached a leaf value.
            flattened_dict[path] = sub_value

    _traverse(value
