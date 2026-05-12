# state_diff_tracker.py

"""
A module for tracking state differences between two dictionary-like objects.

This module provides a function to compute a granular, field-by-field diff
between two states represented as dictionaries.
"""

from typing import Any, Dict, List

# A sentinel object to represent a missing key. This is necessary to distinguish
# between a key that is absent and a key whose value is `None`.
_SENTINEL = object()


def diff_versions(previous: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compares two dictionary versions and returns a list of field-level changes.

    The function identifies modified, added, and removed fields. Each change is
    represented as an explicit dictionary record with 'field', 'before', and
    'after' keys, satisfying State Review Ledger SRL-3. For added fields,
    'before' is None. For removed fields, 'after' is None.

    Args:
        previous: A dictionary representing the old state.
        current: A dictionary representing the new state.

    Returns:
        A list of dictionaries, each detailing a single field change,
        sorted alphabetically by field name.
    """
    # Combine keys from both dictionaries to capture all changes (additions,
    # deletions, and modifications). Sorting ensures the output is ordered
    # by field name as required.
    all_fields = sorted(set(previous.keys()) | set(current.keys()))

    change_records = []

    for field in all_fields:
        # Use a sentinel to safely distinguish a missing key from a key with a
        # value of None.
        before_value = previous.get(field, _SENTINEL)
        after_value = current.get(field, _SENTINEL)

        if before_value != after_value:
            # A change was detected. Create an explicit record for this field.
            # Translate the sentinel to None for the final output record,
            # which is the conventional representation for non-existence.
            record = {
                "field": field,
                "before": before_value if before_value is not _SENTINEL else None,
                "after": after_value if after_value is not _SENTINEL else None,
            }
            change_records.append(record)

    return change_records
