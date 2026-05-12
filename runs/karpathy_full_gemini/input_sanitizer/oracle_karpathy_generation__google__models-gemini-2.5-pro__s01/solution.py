"""
A module for sanitizing a list of field names.
"""

import re


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """Filters a list of field names, returning only those that are allowed and valid.

    The function ensures that the returned fields are:
    1. Present in the `allowed` set.
    2. Composed solely of letters, digits, and underscores.
    3. Unique and in the order of their first appearance in the input list.

    Args:
        fields: A list of strings representing field names to be sanitized.
        allowed: A set of strings representing the allowed field names.

    Returns:
        A new list of strings containing the sanitized, unique, and ordered field names.
    """
    sanitized = []
    seen = set()

    for field in fields:
        if field in seen:
            continue

        # A field is valid if it is in the allowed set and contains only
        # word characters (alphanumeric and underscore). re.fullmatch ensures
        # the entire string matches this pattern.
        if field in allowed and re.fullmatch(r'\w+', field):
            sanitized.append(field)
            seen.add(field)

    return sanitized
