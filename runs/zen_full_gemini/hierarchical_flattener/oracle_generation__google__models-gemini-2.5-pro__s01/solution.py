"""
A module for flattening hierarchical dictionaries into dot-path keys.
"""

from typing import Any, Dict


def flatten_paths(value: Dict[Any, Any]) -> Dict[str, object]:
    """
    Flattens a nested dictionary into a single-level dictionary.

    The keys of the new dictionary are dot-separated paths to the values
    in the original nested structure.

    Lists and empty dictionaries are treated as leaf values and are not
    recursed into. Keys from the original dictionary are converted to
    strings.

    Args:
        value: The dictionary to flatten.

    Returns:
        A new dictionary with flattened keys.

    Raises:
        TypeError: If the input value is not a dictionary.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Input must be a dictionary, but got {type(value).__name__}.")

    flat_dict: Dict[str, object] = {}
    _flatten_recursive(current_dict=value, path_prefix="", result_dict=flat_dict)
    return flat_dict


def _flatten_recursive(
    current_dict: Dict[Any, Any],
    path_prefix: str,
    result_dict: Dict[str, object],
) -> None:
    """
    Recursively processes a dictionary to populate the flattened result.

    This is a helper function that mutates `result_dict` in place.

    Args:
        current_dict: The dictionary to process at the current level.
        path_prefix: The dot-separated path prefix for keys at this level.
        result_dict: The dictionary to populate with flattened key-value pairs.
    """
    for key, value in current_dict.items():
        new_path = _build_path(path_prefix, str(key))

        is_non_empty_dict = isinstance(value, dict) and value
        if is_non_empty_dict:
            _flatten_recursive(
                current_dict=value, path_prefix=new_path, result_dict=result_dict
            )
        else:
            result_dict[new_path] = value


def _build_path(prefix: str, segment: str) -> str:
    """
    Constructs a dot-separated path segment.

    If the prefix is empty, it returns just the segment. Otherwise, it
    joins the prefix and segment with a dot.

    Args:
        prefix: The existing path prefix.
        segment: The new segment to add to the path.

    Returns:
        The combined path string.
    """
    if not prefix:
        return segment
    return f"{prefix}.{segment}"
