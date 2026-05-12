# state_diff_tracker.py
"""A module to track changes between two dictionary-based states."""

from typing import Any, Dict, List

# A sentinel object to represent the absence of a value. This is used to
# distinguish between a field that is not present and a field that has a
# value of None. It is part of the public API of this module.
ABSENT = object()


def diff_versions(
    previous: Dict[str, Any], current: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Compares two dictionary versions and returns a list of field-level changes.

    This function identifies added, removed, and modified fields between the
    `previous` and `current` state dictionaries. Each change is represented
    as a dictionary conforming to the State Review Ledger (SRL-3) format,
    containing 'field', 'before', and 'after' keys.

    The returned list of change records is sorted alphabetically by field name.

    Args:
        previous: A dictionary representing the previous state.
        current: A dictionary representing the current state.

    Returns:
        A sorted list of dictionaries, where each dictionary details a
        single field change. For added fields, the 'before' value will be
        the `state_diff_tracker.ABSENT` sentinel. For removed fields, the
        'after' value will be `state_diff_tracker.ABSENT`.
    """
    all_fields = set(previous.keys()) | set(current.keys())

    changes: List[Dict[str, Any]] = []

    # Iterate through all fields in a sorted order to ensure the output
    # list is sorted by field name, as required.
    for field in sorted(all_fields):
        before_value = previous.get(field, ABSENT)
        after_value = current.get(field, ABSENT)

        # A change is recorded if the before and after values are not identical.
        # This comparison correctly handles additions (where 'before' is ABSENT),
        # removals (where 'after' is ABSENT), and modifications.
        if before_value != after_value:
            change_record = {
                "field": field,
                "before": before_value,
                "after": after_value,
            }
            changes.append(change_record)

    return changes
