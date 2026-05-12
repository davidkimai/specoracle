"""
A module for sanitizing field names based on a set of allowed values and
character constraints.
"""

import re
from typing import List, Set

def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Filters a list of field names, returning only those that are allowed and valid.

    A field is considered valid if it contains only letters (a-z, A-Z),
    digits (0-9), and underscores (_). The function preserves the order of the
    first appearance of each field and removes duplicates.

    Args:
        fields: A list of strings representing field names to be sanitized.
        allowed: A set of strings representing the allowed field names.

    Returns:
        A new list of strings containing the sanitized field names in their
        original order of appearance, with duplicates removed.
    """
    sanitized_list: List[str] = []
    seen: Set[str] = set()

    for field in fields:
        if field in seen:
            continue
        seen.add(field)

        if field not in allowed:
            continue

        # The pattern `\w+` matches one or more word characters, which are
        # letters, digits, and underscores. `re.fullmatch` ensures the entire
        # string consists of only these characters.
        if re.fullmatch(r'\w+', field):
            sanitized_list.append(field)

    return sanitized_list
