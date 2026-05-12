"""
A module for sanitizing input field names based on an allowlist and format.
"""

import re
from typing import List, Set


def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Sanitizes a list of field names based on an allowlist and format constraints.

    The function filters the input list `fields` to produce a new list containing
    only the fields that meet the following criteria:
    1. The field is present in the `allowed` set.
    2. The field contains only ASCII letters, digits, and underscores.
    3. The field is not an empty string.

    The order of the fields in the returned list is preserved from their first
    appearance in the input list. Duplicates are removed.

    Args:
        fields: A list of strings representing the field names to be sanitized.
        allowed: A set of strings representing the allowed field names.

    Returns:
        A new list of sanitized field names, preserving order and removing
        duplicates.
    """
    # This regex pattern ensures that field names consist of one or more
    # ASCII alphanumeric characters or underscores. Anchors ^ and $ ensure
    # the entire string must match. This provides a strict format validation.
    VALID_FIELD_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')

    sanitized_list = []
    seen = set()

    for field in fields:
        if field in seen:
            continue

        # Check against the allowlist first, as set lookups are very fast (O(1) avg).
        # Then, validate the field format against the strict regex.
        if field in allowed and VALID_FIELD_PATTERN.match(field):
            sanitized_list.append(field)
            seen.add(field)

    return sanitized_list
