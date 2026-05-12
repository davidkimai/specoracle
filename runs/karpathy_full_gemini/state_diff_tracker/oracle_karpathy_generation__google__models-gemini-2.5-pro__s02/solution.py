"""
A module for tracking state differences between two dictionary versions.
"""

import typing

# A unique object to represent the absence of a key, distinct from None.
_SENTINEL = object()


def diff_versions(
    previous: typing.Dict[typing.Any, typing.Any],
    current: typing.Dict[typing.Any, typing.Any]
) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Compares two dictionary versions and returns a list of field-level changes.

    This function complies with State Review Ledger (SRL-3) specifications:
    - Every field-level change is represented as an explicit record with
      'field', 'before', and 'after' keys.
    - Multiple changed fields are not collapsed into a summary.

    Each record corresponds to a field that was added, removed, or had its
    value changed. The returned list of records is sorted by field name.

    Args:
        previous: The dictionary representing the previous state.
        current: The dictionary representing the current state.

    Returns:
        A list of change records. For added fields, 'before' is None.
        For removed fields, 'after' is None.
    """
    all_fields = sorted(previous.keys() | current.keys())
    changes = []

    for field in all_fields:
        # Use the sentinel to distinguish a missing key from a key whose value
        # is None. This correctly detects changes when a field with a None
        # value is added or removed.
        before_value = previous.get(field, _SENTINEL)
        after_value = current.get(field, _SENTINEL)

        if before_value != after_value:
            change_record = {
                'field': field,
                'before': None if before_value is _SENTINEL else before_value,
                'after': None if after_value is _SENTINEL else after_value,
            }
            changes.append(change_record)

    return changes
