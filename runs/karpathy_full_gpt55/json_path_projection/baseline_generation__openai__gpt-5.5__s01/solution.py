"""Utilities for projecting fields from nested JSON-like dictionaries."""


_MISSING = object()


def _is_non_negative_integer_text(segment: str) -> bool:
    """Return True if *segment* is an ASCII non-negative integer literal."""
    return segment != "" and all("0" <= char <= "9" for char in segment)


def _resolve_path(record: dict, path: str):
    """
    Resolve a dot-separated path against a JSON-like object.

    Dictionary components are looked up by their string key. List components must
    be non-negative integer indexes written as ASCII decimal digits.
    """
    current = record

    if path == "":
        return current

    for segment in path.split("."):
        if isinstance(current, dict):
            if segment not in current:
                return _MISSING
            current = current[segment]
        elif isinstance(current, list):
            if not _is_non_negative_integer_text(segment):
                return _MISSING
            index = int(segment)
            if index >= len(current):
                return _MISSING
            current = current[index]
        else:
            return _MISSING

    return current


def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    """
    Extract values from *record* according to output-key-to-path mappings.

    Each path is dot-separated and may traverse dictionaries by key and lists by
    non-negative integer index, for example: "orders.0.total". If a path cannot
    be resolved, the corresponding output value is *default*.
    """
    extracted = {}

    for output_key, path in paths.items():
        if not isinstance(path, str):
            extracted[output_key] = default
            continue

        value = _resolve_path(record, path)
        extracted[output_key] = default if value is _MISSING else value

    return extracted
