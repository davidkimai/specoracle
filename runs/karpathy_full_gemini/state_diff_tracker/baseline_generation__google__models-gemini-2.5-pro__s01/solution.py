"""
A module for tracking state differences between two dictionary versions.
"""

from typing import Any, Dict, List

def diff_versions(previous: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compares two dictionary versions and reports the differences.

    This function identifies changes, additions, and removals of fields between
    a 'previous' and 'current' state dictionary.

    Args:
        previous: A dictionary representing the old state.
        current: A dictionary representing the new state.

    Returns:
        A list of dictionaries, where each dictionary represents a single
        field change. Each record contains 'field', 'before', and 'after' keys.
        The list is sorted alphabetically by the 'field' name.
        - For changed values, 'before' and 'after' hold the respective values.
        - For added fields, 'before' is None.
        - For removed fields, 'after' is None.
    """
    all_keys = set(previous.keys()) | set(current.keys())
    diffs: List[Dict[str, Any]] = []

    for key in sorted(all_keys):
        in_previous = key in previous
        in_current = key in current

        if in_previous and in_current:
            # Field exists in both versions.
            prev_val = previous[key]
            curr_val = current[key]
            if prev_val != curr_val:
                diffs.append({
                    "field": key,
                    "before": prev_val,
                    "after": curr_val
                })
        elif in_current:
            # Field was added.
            diffs.append({
                "field": key,
                "before": None,
                "after": current[key]
            })
        else:  # in_previous must be True
            # Field was removed.
            diffs.append({
                "field": key,
                "before": previous[key],
                "after": None
            })

    return diffs
