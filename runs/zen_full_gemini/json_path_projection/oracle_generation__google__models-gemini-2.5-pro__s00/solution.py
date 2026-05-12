#
# Per the Zen of Python:
# - Beautiful is better than ugly.
# - Explicit is better than implicit.
# - Simple is better than complex.
# - Flat is better than nested.
# - Readability counts.
# - Errors should never pass silently.
# - In the face of ambiguity, refuse the temptation to guess.
#
"""A module for extracting data from nested structures using dot-notation paths."""

from typing import Any, Dict, Union


def _resolve_path(
    record: Union[dict, list], path: str, default: Any
) -> Any:
    """
    Traverses a nested structure using a dot-separated path.

    Args:
        record: The dictionary or list to traverse.
        path: The dot-separated path string, e.g., "orders.0.total".
        default: The value to return if the path cannot be resolved.

    Returns:
        The value at the specified path, or the default value.
    """
    segments = path.split('.')
    current_view = record

    for segment in segments:
        if isinstance(current_view, dict):
            try:
                current_view = current_view[segment]
            except KeyError:
                return default
        elif isinstance(current_view, list):
            try:
                index = int(segment)
                current_view = current_view[index]
            except (ValueError, IndexError):
                return default
        else:
            # Cannot traverse further into a non-container type (e.g., int, str).
            return default

    return current_view


def extract_fields(
    record: dict, paths: Dict[str, str], default: Any = None
) -> Dict[str, Any]:
    """
    Extracts values from a nested dictionary based on dot-separated paths.

    Each path specifies a traversal through the record. Path segments can be
    dictionary keys or integer list indexes. If any part of a path cannot be
    resolved, the default value is used for that field.

    Example:
        record = {
            "user": {"name": "Alice", "email": "alice@example.com"},
            "orders": [{"id": 1, "total": 100.50}, {"id": 2, "total": 75.00}]
        }
        paths = {
            "user_name": "user.name",
            "first_order_total": "orders.0.total",
            "third_order_id": "orders.2.id"  # This path will not resolve.
        }
        extracted = extract_fields(record, paths, default="N/A")
        # extracted will be:
        # {
        #     "user_name": "Alice",
        #     "first_order_total": 100.50,
        #     "third_order_id": "N/A"
        # }

    Args:
        record: The input dictionary to extract data from.
        paths: A dictionary mapping desired output keys to dot-separated paths.
        default: The value to use for any path that cannot be resolved.

    Returns:
        A new dictionary containing the extracted values.

    Raises:
        TypeError: If 'record' or 'paths' are not dictionaries, or if the
                   keys or values in 'paths' are not strings.
    """
    if not isinstance(record, dict):
        raise TypeError("record must be a dictionary")
    if not isinstance(paths, dict):
        raise TypeError("paths must be a dictionary")

    result = {}
    for output_key, path in paths.items():
        if not isinstance(output_key, str) or not isinstance(path, str):
            raise TypeError("paths keys and values must be strings")

        value = _resolve_path(record, path, default)
        result[output_key] = value

    return result
