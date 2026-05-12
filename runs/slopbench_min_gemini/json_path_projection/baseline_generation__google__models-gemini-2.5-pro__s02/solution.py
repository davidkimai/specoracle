"""
A module for projecting fields from a nested dictionary using JSON-like paths.
"""

from typing import Any, Dict

def extract_fields(record: Dict[str, Any], paths: Dict[str, str], default: Any = None) -> Dict[str, Any]:
    """
    Extracts values from a nested dictionary based on a map of dot-separated paths.

    Each path is a string with parts separated by dots. Path parts can be
    dictionary keys or integer list indices. If a path cannot be fully resolved
    within the record, the default value is used.

    Args:
        record: The dictionary from which to extract data. This input is not mutated.
        paths: A dictionary mapping desired output keys to their corresponding
               dot-separated path strings within the record.
        default: The value to use for an output key if its path cannot be
                 resolved. Defaults to None.

    Returns:
        A new dictionary mapping each output key from the `paths` argument to
        either the extracted value or the default value.
    """
    result: Dict[str, Any] = {}
    for output_key, path_string in paths.items():
        try:
            current_value: Any = record
            components = path_string.split('.')

            for component in components:
                if isinstance(current_value, list):
                    # Attempt to treat the component as a list index.
                    index = int(component)
                    current_value = current_value[index]
                elif isinstance(current_value, dict):
                    # Treat the component as a dictionary key.
                    current_value = current_value[component]
                else:
                    # The path continues, but the current value is not a
                    # collection that can be indexed further (e.g., a string,
                    # number, or None).
                    raise ValueError("Path leads through a non-collection type.")

            result[output_key] = current_value
        except (KeyError, IndexError, ValueError, TypeError):
            # KeyError: A dictionary key in the path was not found.
            # IndexError: A list index in the path was out of bounds.
            # ValueError: A component for a list was not a valid integer, or
            #             the path led through a non-traversable type.
            # TypeError: Attempted to index an object that is not indexable
            #            (e.g., a None value encountered mid-path).
            result[output_key] = default

    return result
