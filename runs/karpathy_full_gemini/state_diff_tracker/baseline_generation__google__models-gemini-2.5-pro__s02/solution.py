"""
This module provides a function to compute the difference between two dictionary-based states.
"""

from typing import Any, Dict, List


def diff_versions(previous: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compares two dictionaries and returns a list of differences.

    This function identifies fields that have been added, removed, or had their
    values changed between the `previous` and `current` dictionary states.

    Args:
        previous: A dictionary representing the old state.
        current: A dictionary representing the new state.

    Returns:
        A list of dictionaries, where each dictionary represents a single
        field change. Each record has the following keys:
        - 'field': The name of the field that changed.
        - 'before': The value of the field in the `previous` state. This is
                    None if the field was added.
        - 'after': The value of the field in the `current` state. This is
                   None if the field was removed.
        The list is sorted alphabetically by the 'field' name.
    """
    changes: List[Dict[str, Any]] = []

    # Combine all keys from both dictionaries to ensure we check every field.
    all_keys = set(previous.keys()) | set(current.keys())

    # Iterate through keys in sorted order to meet the sorting requirement.
    for key in sorted(all_keys):
        key_in_prev = key in previous
        key_in_curr = key in current

        if key_in_prev and key_in_curr:
            # Case 1: Field exists in both versions. Check if the value changed.
            if previous[key] != current[key]:
                changes.append({
                    'field': key,
                    'before': previous[key],
                    'after': current[key]
                })
        elif key_in_curr:
            # Case 2: Field was added (only in current).
            changes.append({
                'field': key,
                'before': None,
                'after': current[key]
            })
        else:  # key_in_prev must be True
            # Case 3: Field was removed (only in previous).
            changes.append({
                'field': key,
                'before': previous[key],
                'after': None
            })

    return changes
