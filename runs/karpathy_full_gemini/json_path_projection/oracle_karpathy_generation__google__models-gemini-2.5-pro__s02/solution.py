import typing

def extract_fields(record: dict, paths: dict[str, str], default: typing.Any = None) -> dict:
    """
    Extracts values from a nested dictionary/list structure based on dot-separated paths.

    Each path in the `paths` dictionary is resolved against the `record`. If a path
    cannot be fully resolved (e.g., due to a missing key, an out-of-bounds index,
    or an attempt to index a non-indexable type), the `default` value is used.

    Args:
        record: The dictionary structure to extract data from. The structure may
                contain nested lists.
        paths: A dictionary mapping output keys to dot-separated path strings.
               Path components can be dictionary keys or integer list indices.
               Example: {"order_total": "orders.0.total"}
        default: The value to return for a path that cannot be resolved.

    Returns:
        A dictionary mapping each output key from the `paths` input to its
        extracted value or the default value.
    """

    def _resolve_path(data: typing.Any, path: str) -> typing.Any:
        """
        Safely resolves a dot-separated path against a data structure, returning
        the default value on failure.
        """
        current_value = data
        components = path.split('.')
        for component in components:
            try:
                if isinstance(current_value, list):
                    # Attempt to access by integer index
                    current_value = current_value[int(component)]
                elif isinstance(current_value, dict):
                    # Attempt to access by key
                    current_value = current_value[component]
                else:
                    # Cannot traverse further into non-collection types
                    return default
            except (KeyError, IndexError, ValueError, TypeError):
                # KeyError: dict key does not exist.
                # IndexError: list index is out of bounds.
                # ValueError: component cannot be converted to an int for list access.
                # TypeError: `current_value` is not indexable (e.g., None).
                return default
        return current_value

    return {
        output_key: _resolve_path(record, path_string)
        for output_key, path_string in paths.items()
    }
