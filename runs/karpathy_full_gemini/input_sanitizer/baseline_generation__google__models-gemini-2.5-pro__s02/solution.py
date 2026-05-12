"""
A module for sanitizing input field names based on an allowlist and format constraints.
"""

import re
from typing import List, Set

def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Filters a list of field names, returning only those that are allowed and
    syntactically valid.

    The function ensures that the returned fields:
    1. Are present in the `allowed` set.
    2. Contain only ASCII letters, digits, and underscores.
    3. Are unique, with order preserved from the first appearance in the input list.

    Args:
        fields: A list of strings representing field names to sanitize.
        allowed: A set of strings representing the allowed field names.

    Returns:
        A list of sanitized field names.
    """
    # This regex ensures that field names consist of one or more ASCII
    # alphanumeric characters or underscores. `re.fullmatch` anchors the
    # pattern to the beginning and end of the string.
    valid_field_pattern = re.compile(r'[a-zA-Z0-9_]+')

    sanitized = []
    seen = set()

    for field in fields:
        if not isinstance(field, str):
            continue

        if field in seen:
            continue

        if field in allowed and valid_field_pattern.fullmatch(field):
            sanitized.append(field)
            seen.add(field)

    return sanitized
