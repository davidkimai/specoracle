"""
A module for flattening nested dictionary structures into dot-path keys.
"""

from typing import Any, Dict, List


def _validate_and_get_str_key(key: Any) -> str:
    """
    Validates that a dictionary key is a string and does not contain dots.

    Args:
        key: The dictionary key to validate.

    Returns:
        The key as a string if it is valid.

    Raises:
        TypeError: If the key is not a string.
        ValueError: If the key contains a dot ('.').
    """
    if not isinstance(key, str):
        raise TypeError(
            f"Dictionary keys must be strings for flattening, but received "
            f"key of type {type(key).__name__}."
        )
    if '.' in key:
        raise ValueError(
            f"Dictionary keys cannot contain '.' characters for flattening, but "
            f"found key: '{key}'"
        )
    return key


def _flatten_recursively(
    current_value: Any,
    path_parts: List[str],
    flattened_map: Dict[str, object]
) -> None:
    """
    Recursively traverses a data structure, building a flattened map.

    This helper mutates the `flattened_map` dictionary as it traverses.

    Args:
        current_value: The value to process (can be a dict or a leaf).
        path_parts: The list of string keys forming the path to the current value.
        flattened_map: The dictionary being built with flattened key-value pairs.
    """
    if isinstance(current_value, dict):
        for key, value in current_value.items():
            str_key = _validate_and_get_str_key(key)
            new_path_parts = path_parts + [str_key]
            _flatten_recursively(value, new_path_parts, flattened_map)
    else:
        # This branch handles leaf values. Per requirements, lists are leaves.
        # The path_parts list is guaranteed to be non-empty because the root
        # value must be a dictionary, so leaves are always nested.
        path = ".".join(path_parts)
        flattened_map[path] = current_value


def flatten_paths(value: dict) -> Dict[str, object]:
    """
    Flattens a nested dictionary into a single-level dictionary.

    The keys of the new dictionary are dot-separated paths that represent the
    nesting in the original dictionary. Per requirements, lists are treated as
    leaf values and are not traversed.

    Example:
        >>> data = {'a': {'b': 1}, 'c': [2, 3], 'd': {'e': {}}}
        >>> flatten_paths(data)
        {'a.b': 1, 'c': [2, 3]}

    Args:
        value: The dictionary to flatten. All keys in the nested structure
               must be strings.

    Returns:
        A new dictionary with dot-path keys and their corresponding values.

    Raises:
        TypeError: If the input `value` is not a dictionary, or if any key
                   within the nested structure is not a string.
        ValueError: If any string key contains a dot ('.'), as this would
                    create ambiguity in the flattened paths.
    """
    if not isinstance(value, dict):
        raise TypeError(
            f"The input value must be a dictionary, but received "
            f"type {type(value).__name__}."
        )

    result: Dict[str, object] = {}
    _flatten_recursively(value, [], result)
    return result
