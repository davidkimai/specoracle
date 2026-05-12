"""
hierarchical_flattener.py

Provides flatten_paths(value: dict) -> dict[str, object].

Flattens nested dictionaries into a single-level dictionary whose keys are
dot-separated paths representing the original nesting hierarchy.  Lists (and
all other non-dict types) are treated as leaf values and are kept as-is.
"""

from __future__ import annotations


def flatten_paths(value: dict, _prefix: str = "") -> dict[str, object]:
    """Flatten a nested dict into dot-path keys.

    Parameters
    ----------
    value:
        The (possibly nested) dictionary to flatten.
    _prefix:
        Internal parameter used during recursion to track the current path
        prefix.  Callers should not pass this argument.

    Returns
    -------
    dict[str, object]
        A flat dictionary where every key is a dot-joined path string and
        every value is a non-dict leaf value (int, str, list, None, …).

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}

    >>> flatten_paths({})
    {}
    """
    if not isinstance(value, dict):
        raise TypeError(
            f"flatten_paths expects a dict as its first argument, got {type(value).__name__!r}"
        )

    result: dict[str, object] = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            # Recurse into nested dicts.
            nested = flatten_paths(val, _prefix=full_key)
            result.update(nested)
        else:
            # Leaf value (including lists, primitives, None, etc.)
            result[full_key] = val

    return result
