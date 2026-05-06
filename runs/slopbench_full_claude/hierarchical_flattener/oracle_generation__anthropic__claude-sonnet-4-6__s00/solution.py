"""
hierarchical_flattener.py

Flatten a nested dict into a single-level dict with dot-separated keys.
Lists are treated as leaf values and are not recursed into.
"""


def flatten_paths(value: dict) -> dict[str, object]:
    """Return a flat dict mapping dot-path keys to leaf values.

    Args:
        value: A (possibly nested) dictionary to flatten.

    Returns:
        A new dict where every key is a dot-joined path string and every
        value is a non-dict leaf (including lists, scalars, None, etc.).

    Raises:
        TypeError: If *value* is not a dict.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Expected a dict, got {type(value).__name__!r}")

    result: dict[str, object] = {}
    _collect(value, prefix="", out=result)
    return result


def _collect(node: dict, prefix: str, out: dict[str, object]) -> None:
    """Recursively walk *node*, writing dot-path entries into *out*."""
    for key, child in node.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict):
            if child:
                _collect(child, path, out)
            else:
                # Preserve empty dicts as leaf values.
                out[path] = child
        else:
            out[path] = child
