# -*- coding: utf-8 -*-
"""
A module for extracting data from nested structures using dot-separated paths.

This module provides a single function, `extract_fields`, which allows for
the projection of a nested dictionary or list structure into a flat dictionary
based on a set of specified paths.
"""

from typing import Any, Dict


class PathResolutionError(Exception):
    """Raised when a path cannot be resolved within a record."""
    pass


def _get_value_by_path(record: object, path: str) -> Any:
    """
    Traverses a nested structure using a dot-separated path.

    Args:
        record: The dict or list to traverse.
        path: The dot-separated path string. An empty string returns the record.

    Returns:
        The value found at the specified path.

    Raises:
        PathResolutionError: If the path is invalid or cannot be resolved at any
                             step of the traversal.
    """
    if not path:
        return record

    parts = path.split('.')
    current_value = record

    for part in parts:
        if isinstance(current_value, dict):
            if part not in current_value:
                raise PathResolutionError(f"Key '{part}' not found in dictionary.")
            current_value = current_value[part]

        elif isinstance(current_value, list):
            try:
                index = int(part)
            except ValueError:
                msg = f"Path part '{part}' is not a valid integer index for a list."
                raise PathResolutionError(msg) from None

            try:
                current_value = current_value[index]
            except IndexError:
                msg = f"Index {index} is out of bounds for list of size {len(current_value)}."
                raise PathResolutionError(msg) from None
        else:
            msg = f"Cannot traverse into non-collection type '{type(current_value).__name__}' with part '{part}'."
            raise PathResolutionError(msg)

    return current_value


def extract_fields(
    record: Dict[str, Any],
    paths: Dict[str, str],
    default: Any = None
) -> Dict[str, Any]:
    """
    Extracts fields from a nested dictionary based on a mapping of keys to paths.

    Each path is a dot-separated string that may include integer list indexes,
    such as "orders.0.total". If a path cannot be resolved, the default value is
    used. The input record is not mutated.

    Args:
        record: The dictionary from which to extract values.
        paths: A dictionary mapping output keys to dot-separated path strings.
        default: The value to use for paths that cannot be resolved.

    Returns:
        A dictionary containing the extracted values, keyed by the output keys
        from the 'paths' dictionary.

    Raises:
        TypeError: If 'record' or 'paths' are not dictionaries, or if a path
                   value in 'paths' is not a string.
    """
    if not isinstance(record, dict):
        raise TypeError("Input 'record' must be a dictionary.")
    if not isinstance(paths, dict):
        raise TypeError("Input 'paths' must be a dictionary.")

    extracted_data = {}
    for output_key, path in paths.items():
        if not isinstance(path, str):
            msg = f"Path for key '{output_key}' must be a string, not {type(path).__name__}."
            raise TypeError(msg)

        try:
            value = _get_value_by_path(record, path)
            extracted_data[output_key] = value
        except PathResolutionError:
            extracted_data[output_key] = default

    return extracted_data
