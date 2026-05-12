"""A module for flattening hierarchical data structures."""


def flatten_paths(value: dict) -> dict[str, object]:
    """
    Flattens a nested dictionary into a single-level dictionary with dot-path keys.

    Keys at each level of nesting are joined by a dot '.' to form the new key.
    Non-string keys will be converted to strings.

    Lists and other non-dict objects are treated as leaf values and are not
    traversed. For example: `{'a': {'b': [1, 2]}}` becomes `{'a.b': [1, 2]}`.

    An empty dictionary at any level will not produce any output keys. For example:
    `{'a': {'b': {}}, 'c': 1}` becomes `{'c': 1}`.

    Args:
        value: The nested dictionary to flatten.

    Returns:
        A new dictionary with flattened key-value pairs.

    Raises:
        TypeError: If the input `value` is not a dictionary.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Input must be a dictionary, but got {type(value).__name__}.")

    flat_dict: dict[str, object] = {}

    def _flatten_recursive(current_obj: object, path_prefix: str) -> None:
        """
        Recursively traverses the object and populates the flat_dict.

        Args:
            current_obj: The current object to process (can be a dict or a leaf).
            path_prefix: The dot-separated path to the current object.
        """
        if isinstance(current_obj, dict):
            # If the dictionary is empty, this loop will not run, effectively
            # ending the traversal for this path.
            for key, val in current_obj.items():
                new_prefix = f"{path_prefix}.{key}" if path_prefix else str(key)
                _flatten_recursive(val, new_prefix)
        else:
            # Reached a leaf value (i.e., not a dictionary).
            # The path_prefix should not be empty unless the top-level value
            # was not a dictionary, which is handled by the initial check.
            if path_prefix:
                flat_dict[path_prefix] = current_obj

    _flatten_recursive(value, "")
    return flat_dict
