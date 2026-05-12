"""
A module for sanitizing input field names.
"""

import re
from typing import List, Set

# A pre-compiled regular expression for validating field names.
# A valid field name consists of one or more letters (a-z, A-Z),
# digits (0-9), or underscores (_). The pattern `\w+` matches this set.
# The `^` and `$` anchors ensure the entire string must match.
_VALID_FIELD_PATTERN = re.compile(r"^\w+$")


def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Filters a list of strings, returning fields that are allowed and valid.

    The function processes an input list of field names and returns a new list
    containing only the fields that meet two criteria:
    1. The field must be present in the `allowed` set.
    2. The field must contain only alphanumeric characters and underscores.

    This function preserves the relative order of the first appearance of each
    valid field from the input list and removes any subsequent duplicates.

    Args:
        fields: A list of strings, representing the field names to sanitize.
        allowed: A set of strings, representing the whitelist of allowed field
                 names.

    Returns:
        A list of sanitized field names.
    """
    sanitized_fields = []
    seen = set()
    for field in fields:
        if field in seen:
            continue
        if field in allowed and _VALID_FIELD_PATTERN.match(field):
            sanitized_fields.append(field)
            seen.add(field)
    return sanitized_fields
