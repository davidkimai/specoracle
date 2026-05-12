import typing

def extract_fields(
    record: dict, paths: typing.Dict[str, str], default: typing.Any = None
) -> dict:
    """Extracts values from a nested dictionary-like object using dot-separated paths.

    Each path in the `paths` dictionary is a string of keys and list indexes
    separated by dots, e.g., "orders.0.total". The function navigates through
    the `record` to find the corresponding value. The input record is not mutated.

    Args:
        record: The dictionary (or nested structure of dicts and lists) to
                extract data from.
        paths: A dictionary mapping the desired output key to the dot-separated
               path string used for extraction.
        default: The value to return for a given path if it cannot be fully
                 resolved (e.g., a key or index does not exist). Defaults to None.

    Returns:
        A new dictionary where each key is from the input `paths` dictionary
        and each value is the extracted value from the record, or the default
        value if the path was not found.
    """

    def _resolve_path(data: dict, path: str) -> typing.Any:
        """
        Safely traverses the data structure according to the path.
        Returns the default value if any part of the path is invalid.
        """
        parts = path.split('.')
        current_item = data
        for part in parts:
            try:
                if isinstance(current_item, dict):
                    current_item = current_item[part]
                elif isinstance(current_item, list):
                    index = int(part)
                    current_item = current_item[index]
                else:
                    # Cannot traverse further into non-collection types.
                    return default
            except (KeyError, IndexError, ValueError, TypeError):
                # KeyError: dict key does not exist.
                # IndexError: list index is out of bounds.
                # ValueError: part cannot be converted to an int for list access.
                # TypeError: tried to index a non-indexable object (e.g., None).
                return default
        return current_item

    return {key: _resolve_path(record, path) for key, path in paths.items()}
