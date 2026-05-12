#
# Copyright (c) 2024, Safe Synthesis Inc.
# All rights reserved.
#
#
"""
A utility for projecting fields from a nested data structure using dot-notation paths.
"""
from __future__ import annotations

from typing import Any, Dict


def extract_fields(record: dict, paths: dict[str, str], default: Any = None) -> dict:
    """
    Extracts values from a nested dictionary/list structure based on dot-separated paths.

    Each path is a dot-separated string that may include integer list indexes,
    such as "orders.0.total". This function navigates the structure according
    to the path for each key in the `paths` dictionary.

    Args:
        record: The dictionary structure to extract data from. The input is not mutated.
        paths: A dictionary mapping desired output keys to their corresponding
               dot-separated paths within the record.
        default: The value to use for an output key if its corresponding path
                 cannot be fully resolved within the record.

    Returns:
        A new dictionary mapping each output key from the `paths` argument to
        its extracted value. If a path is invalid or does not exist in the
        record, the `default` value is used for that key.
    """
    # The type hints use `dict` as per the prompt's signature style (PEP 585),
    # assuming a modern Python environment (3.9+). The implementation itself
    # is compatible with older versions of Python 3.
    result: dict[str, Any] = {}

    for output_key, path_string in paths.items():
        try:
            current_value: Any = record
            parts = path_string.split('.')

            for part in parts:
                if isinstance(current_value, dict):
                    # Path part is a dictionary key.
                    current_value = current_value[part]
                elif isinstance(current_value, list):
                    # Path part is a list index.
                    index = int(part)
                    current_value = current_value[index]
                else:
                    # The path cannot be traversed further because the current value
                    # is not a collection (e.g., it's a string, number, or None).
                    # We raise an error to be caught by the common exception handler.
                    raise TypeError("Path resolution failed on a non-collection type.")

            # If the loop completes, the path was successfully resolved.
            result[output_key] = current_value

        except (KeyError, IndexError, ValueError, TypeError):
            # A failure occurred during path resolution:
            # - KeyError: A dictionary key was not found.
            # - IndexError: A list index was out of bounds.
            # - ValueError: A path part intended as an index was not a valid integer.
            # - TypeError: An attempt was made to index a non-collection type.
            result[output_key] = default

    return result
