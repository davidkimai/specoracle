# -*- coding: utf-8 -*-
"""
A module for extracting data from nested structures using dot-separated paths.
"""

import typing

__all__ = ["extract_fields"]


def _resolve_path(
    record: typing.Any, path_string: str, default: typing.Any
) -> typing.Any:
    """
    Resolves a dot-separated path against a nested data structure.

    Args:
        record: The dictionary or list to traverse.
        path_string: A dot-separated string representing the path.
        default: The value to return if the path cannot be resolved.

    Returns:
        The resolved value, or the default if resolution fails at any point.
    """
    segments = path_string.split('.')
    current_node = record

    for segment in segments:
        if isinstance(current_node, dict):
            if segment not in current_node:
                return default
            current_node = current_node[segment]
        elif isinstance(current_node, list):
            try:
                index = int(segment)
                current_node = current_node[index]
            except (ValueError, IndexError):
                return default
        else:
            # Cannot traverse further (e.g., current_node is a primitive),
            # but there are more path segments left to process.
            return default

    return current_node


def extract_fields(
    record: dict, paths: typing.Dict[str, str], default: typing.Any = None
) -> dict:
    """
    Extracts values from a nested dictionary based on a map of paths.

    Each path is a dot-separated string that may include integer list indexes,
    such as "orders.0.total".

    Args:
        record: The input dictionary to extract data from.
        paths: A dictionary mapping output keys to dot-separated paths.
        default: The value to use for any path that cannot be resolved.

    Returns:
        A dictionary mapping each output key to the extracted value.

    Raises:
        TypeError: If `record` or `paths` are not dictionaries, or if any
                   path in `paths` is not a string.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dictionary, not {type(record).__name__}.")
    if not isinstance(paths, dict):
        raise TypeError(f"paths must be a dictionary, not {type(paths).__name__}.")

    extracted_data = {}
    for output_key, path in paths.items():
        if not isinstance(path, str):
            raise TypeError(
                f"Path for key '{output_key}' must be a string, "
                f"not {type(path).__name__}."
            )

        value = _resolve_path(record, path, default)
        extracted_data[output_key] = value

    return extracted_data
