import typing

def extract_fields(
    record: dict, paths: typing.Dict[str, str], default: typing.Any = None
) -> dict:
    """
    Extracts fields from a nested data structure based on dot-separated paths.

    Each path is a string of keys and indexes joined by dots, e.g.,
    "orders.0.total". This function traverses the input `record` according
    to these paths.

    Args:
        record: The dictionary or list structure to extract data from.
        paths: A dictionary mapping desired output keys to their corresponding
               dot-separated paths within the record.
        default: The value to return for a path that cannot be resolved.
                 This can happen if a key or index does not exist at any
                 point along the path.

    Returns:
        A dictionary where each key is from the input `paths` dictionary and
        each value is the data extracted from the `record` at the specified
        path, or the `default` value if the path was not found.

    Example:
        >>> data = {
        ...     "user": {"name": "Alice", "id": 123},
        ...     "orders": [{"id": "a", "total": 100}, {"id": "b", "total": 200}]
        ... }
        >>> path_map = {
        ...     "user_name": "user.name",
        ...     "first_order_total": "orders.0.total",
        ...     "shipping_address": "user.address.street"
        ... }
        >>> extract_fields(data, path_map, default="N/A")
        {'user_name': 'Alice', 'first_order_total': 100, 'shipping_address': 'N/A'}
    """
    results = {}
    for output_key, path in paths.items():
        try:
            current_value = record
            for part in path.split("."):
                if isinstance(current_value, list):
                    # For lists, the path part must be a valid integer index.
                    current_value = current_value[int(part)]
                elif isinstance(current_value, dict):
                    # For dicts, the path part is a key.
                    current_value = current_value[part]
                else:
                    # Path leads to a non-traversable type (e.g., int, str).
                    # We cannot continue, so we treat the path as unresolved.
                    raise TypeError("Path traverses a non-indexable object.")
            results[output_key] = current_value
        except (KeyError, IndexError, ValueError, TypeError):
            # Any of these exceptions indicates the path could not be resolved.
            # - KeyError: A dictionary key was not found.
            # - IndexError: A list index was out of bounds.
            # - ValueError: A path part for a list was not a valid integer.
            # - TypeError: Attempted to index a non-indexable object.
            results[output_key] = default
    return results
