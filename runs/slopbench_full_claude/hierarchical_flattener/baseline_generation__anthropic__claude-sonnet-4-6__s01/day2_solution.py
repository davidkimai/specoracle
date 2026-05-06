"""
hierarchical_flattener.py

Flatten nested dictionaries into dot-path keys.
Lists are treated as leaf values by default; use array_mode='index' to expand them.
"""


def flatten_paths(value: dict, _prefix: str = "", array_mode: str = "leaf") -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary with dot-separated keys.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to build the key path.
        Callers should not pass this argument.
    array_mode : str
        Controls how list values are handled:
        - 'leaf'  (default): lists are kept as-is, treated as leaf values.
        - 'index': list items are expanded using bracket notation, e.g. users[0].name.

    Returns
    -------
    dict[str, object]
        A flat dictionary where each key is a dot-separated path string
        representing the original nesting hierarchy, and each value is a
        non-dict leaf value.

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}

    >>> flatten_paths({"users": [{"name": "Alice"}, {"name": "Bob"}]}, array_mode='index')
    {'users[0].name': 'Alice', 'users[1].name': 'Bob'}

    >>> flatten_paths({"nums": [1, 2, 3]}, array_mode='index')
    {'nums[0]': 1, 'nums[1]': 2, 'nums[2]': 3}
    """
    if not isinstance(value, dict):
        raise TypeError(
            f"flatten_paths expects a dict as its first argument, got {type(value).__name__!r}"
        )
    if array_mode not in ("leaf", "index"):
        raise ValueError(f"array_mode must be 'leaf' or 'index', got {array_mode!r}")

    result: dict = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            nested = flatten_paths(val, _prefix=full_key, array_mode=array_mode)
            result.update(nested)
        elif isinstance(val, list) and array_mode == "index":
            _flatten_list(val, full_key, result, array_mode)
        else:
            result[full_key] = val

    return result


def _flatten_list(lst: list, prefix: str, result: dict, array_mode: str) -> None:
    """
    Recursively expand a list into indexed keys, writing into *result* in place.

    Parameters
    ----------
    lst : list
        The list to expand.
    prefix : str
        The key prefix built so far (e.g. 'users').
    result : dict
        The accumulator dictionary to write leaf values into.
    array_mode : str
        Passed through so that nested lists/dicts are handled consistently.
    """
    for i, item in enumerate(lst):
        indexed_key = f"{prefix}[{i}]"
        if isinstance(item, dict):
            nested = flatten_paths(item, _prefix=indexed_key, array_mode=array_mode)
            result.update(nested)
        elif isinstance(item, list):
            _flatten_list(item, indexed_key, result, array_mode)
        else:
            result[indexed_key] = item
