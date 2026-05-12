# -*- coding: utf-8 -*-
"""
A module for extracting data from nested structures using dot-notation paths.
"""

from typing import Any, Dict, List


def _resolve_path(source_obj: Any, path_string: str, default: Any) -> Any:
    """
    Safely resolves a dot-separated path against a nested object.

    Args:
        source_obj: The object to traverse (e.g., a dict or list).
        path_string: The dot-separated path to resolve.
        default: The value to return if the path cannot be resolved.

    Returns:
        The resolved value, or the default if resolution fails at any step.
    """
    parts = path_string.split('.')
    current_value = source_obj

    for part in parts:
        if isinstance(current_value, dict):
            try:
                current_value = current_value[part]
            except KeyError:
                return default
        elif isinstance(current_value, list):
            try:
                index = int(part)
                current_value = current_value[index]
            except (ValueError, IndexError):
                return default
        else:
            # Cannot traverse further into non-collection types.
            return default

    return current_value


def extract_fields(
    record: Dict[str, Any],
    paths: Dict[str, str],
    default: Any = None,
) -> Dict[str, Any]:
    """
    Extracts specified fields from a nested dictionary using dot-notation paths.

    Each path is a dot-separated string that may include integer list indexes,
    such as "orders.0.total". This function returns a new dictionary that maps
    each key from the `paths` dictionary to its corresponding extracted value
    from the `record`.

    Args:
        record: The dictionary from which to extract data.
        paths: A dictionary mapping desired output keys to their dot-separated
               path strings inside the record.
        default: The value to use for a path that cannot be resolved.
                 Defaults to None.

    Returns:
        A new dictionary containing the extracted key-value pairs.

    Raises:
        TypeError: If `record` or `paths` are not dictionaries, or if a path
                   in `paths` is not a string.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dictionary, not {type(record).__name__}.")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dictionary, not {type(paths).__name__}.")

    projection = {}
    for output_key, path_string in paths.items():
        if not isinstance(path_string, str):
            raise TypeError(
                f"Path for key '{output_key}' must be a string, "
                f"not {type(path_string).__name__}."
            )

        value = _resolve_path(record, path_string, default)
        projection[output_key] = value

    return projection
