"""
hierarchical_flattener.py

Flatten a nested dict into a single-level dict with dot-separated keys.
Lists are treated as leaf values by default (array_mode='leaf').
When array_mode='index', list items are recursed into using bracket-index
notation, e.g. users[0].name.
"""


def flatten_paths(value: dict, array_mode: str = "leaf") -> dict[str, object]:
    """Return a flat dict mapping dot-path keys to leaf values.

    Args:
        value: A (possibly nested) dictionary to flatten.
        array_mode: Controls list handling.
            'leaf'  – lists are treated as opaque leaf values (default).
            'index' – lists are recursed into; each item's key is formed
                      with bracket notation, e.g. ``items[0].sub``.

    Returns:
        A new dict where every key is a dot-joined path string and every
        value is a non-dict (and, when array_mode='index', non-list) leaf.

    Raises:
        TypeError: If *value* is not a dict.
        ValueError: If *array_mode* is not 'leaf' or 'index'.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Expected a dict, got {type(value).__name__!r}")
    if array_mode not in ("leaf", "index"):
        raise ValueError(f"array_mode must be 'leaf' or 'index', got {array_mode!r}")

    result: dict[str, object] = {}
    _collect(value, prefix="", out=result, array_mode=array_mode)
    return result


def _collect(
    node: dict, prefix: str, out: dict[str, object], array_mode: str
) -> None:
    """Recursively walk *node*, writing dot-path entries into *out*."""
    for key, child in node.items():
        path = f"{prefix}.{key}" if prefix else key
        _emit(child, path, out, array_mode)


def _emit(child: object, path: str, out: dict[str, object], array_mode: str) -> None:
    """Emit *child* (reached via *path*) into *out*, recursing as needed."""
    if isinstance(child, dict):
        if child:
            _collect(child, path, out, array_mode)
        else:
            # Preserve empty dicts as leaf values.
            out[path] = child
    elif isinstance(child, list) and array_mode == "index":
        if child:
            for idx, item in enumerate(child):
                indexed_path = f"{path}[{idx}]"
                _emit(item, indexed_path, out, array_mode)
        else:
            # Preserve empty lists as leaf values.
            out[path] = child
    else:
        out[path] = child
