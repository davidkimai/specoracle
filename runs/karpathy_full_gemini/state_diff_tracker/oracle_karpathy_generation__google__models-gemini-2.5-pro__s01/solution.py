# state_diff_tracker.py
"""
A module for tracking field-level changes between two dictionary-based states.
"""

import typing

__all__ = ["diff_versions", "FIELD_ABSENT"]


# A sentinel object to represent a field that is not present in a state version.
# This is used to distinguish from a field that is present with a value of `None`.
FIELD_ABSENT: typing.Final = object()


def diff_versions(
    previous: typing.Dict[str, typing.Any],
    current: typing.Dict[str, typing.Any],
) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Computes the field-level differences between two state dictionaries.

    This function adheres to State Review Ledger SRL-3:
    - Every field-level change must be represented as an explicit record
      with 'field', 'before', and 'after'.
    - Multiple changed fields are not collapsed into a summary.

    Args:
        previous: The dictionary representing the old state.
        current: The dictionary representing the new state.

    Returns:
        A list of records, sorted by field name. Each record represents a
        single changed, added, or removed field and is a dictionary with keys
        'field', 'before', and 'after'. The value for a non-existent field
        is the `FIELD_ABSENT` sentinel.
    """
    all_fields = sorted(previous.keys() | current.keys())

    diff_records = []
    for field in all_fields:
        before_value = previous.get(field, FIELD_ABSENT)
        after_value = current.get(field, FIELD_ABSENT)

        if before_value != after_value:
            diff_records.append(
                {
                    "field": field,
                    "before": before_value,
                    "after": after_value,
                }
            )

    return diff_records
