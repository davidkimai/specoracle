"""
hierarchical_flattener.py

Provides flatten_paths(value: dict) -> dict[str, object], which flattens
nested dicts into dot-separated path keys.  Lists are treated as leaf values.
"""

from __future__ import annotations


def flatten_paths(value: dict, _prefix: str = "") -> dict[str, object]:
    """Flatten a nested dict into a dict with dot-path keys.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to build the key prefix.
        Callers should not pass this argument.

    Returns
    -------
    dict[str, object]
        A flat dictionary whose keys are dot-separated paths corresponding to
        the original nested structure.  Lists and all non-dict values are kept
        as-is (leaf values).

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}
    """
    if not isinstance(value, dict):
        raise TypeError(f"flatten_paths expects a dict at the top level, got {type(value).__name__!r}")

    result: dict[str, object] = {}
    _flatten(value, _prefix, result)
    return result


def _flatten(node: object, prefix: str, accumulator: dict[str, object]) -> None:
    """Recursive helper that writes flattened entries into *accumulator*."""
    if isinstance(node, dict):
        for key, child in node.items():
            full_key = f"{prefix}.{key}" if prefix else key
            _flatten(child, full_key, accumulator)
    else:
        # Leaf value (including lists, scalars, None, etc.)
        accumulator[prefix] = node
