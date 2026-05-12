"""
A module for extracting data from nested structures using dot-notation paths.
"""

import collections.abc
from typing import Any, Dict, Optional


def extract_fields(
    record: Dict[str, Any],
    paths: Dict[str, str],
    default: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Extracts values from a nested dictionary based on a map of dot-separated paths.

    Each path is a string of keys and list indexes separated by dots,
    e.g., "orders.0.total".

    Args:
        record: The dictionary to extract data from. This input is not mutated.
        paths: A dictionary mapping desired output keys to their corresponding
               dot-separated paths within the record.
        default: The value to use for any path that cannot be fully resolved.
                 Defaults to None.

    Returns:
        A new dictionary mapping each output key to its extracted value.
        If a path cannot be resolved, the default value is used.
    """

    def _resolve_path(current_obj: Any, path_str: str) -> Any:
        """
        Retrieves a value from a nested object using a dot-separated path.

        Returns the `default` value from the outer scope if the path is not found.
        """
        parts = path_str.split(".")
        for part in parts:
            if isinstance(current_obj, collections.abc.Mapping):
                try:
                    current_obj = current_obj[part]
                except KeyError:
                    return default
            elif isinstance(
                current_obj, collections.abc.Sequence
            ) and not isinstance(current_obj, (str, bytes)):
                try:
                    index = int(part)
                    current_obj = current_obj[index]
                except (ValueError, IndexError):
                    return default
            else:
                # The current object is not a collection we can traverse further.
                return default
        return current_obj

    result: Dict[str, Any] = {}
    for output_key, path in paths.items():
        result[output_key] = _resolve_path(record, path)
    return result
