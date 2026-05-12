# state_diff_tracker.py
"""A module for tracking state differences between two dictionary versions."""

from __future__ import annotations

from typing import Any, Dict, List, Set

# SRL-3: Every field-level change must be represented as an explicit record.
# To unambiguously represent the addition or removal of a field, a sentinel
# object is used. This distinguishes the absence of a key from a key whose
# value is `None`.


class _Missing:
    """Sentinel class for a value that is not present in a dictionary."""

    def __repr__(self) -> str:
        return "<MISSING>"


MISSING: Any = _Missing()
"""A sentinel object representing the absence of a key in a dictionary."""


def diff_versions(
    previous: Dict[str, Any], current: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Compares two dictionary versions and returns a list of field-level changes.

    This function adheres to State Review Ledger SRL-3. Each change is an
    explicit record with 'field', 'before', and 'after' values. This includes
    fields that were added or removed. The absence of a field is represented
    by the `state_diff_tracker.MISSING` sentinel object.

    The returned list of changes is sorted alphabetically by field name.

    Args:
        previous: The dictionary representing the previous state.
        current: The dictionary representing the current state.

    Returns:
        A list of dictionaries, where each dictionary details a single
        field change.
    """
    # Combine keys from both dictionaries to get the full set of fields to check.
    all_fields: Set[str] = set(previous.keys()) | set(current.keys())

    diff_records: List[Dict[str, Any]] = []

    # Iterate through all unique fields, sorted alphabetically, to ensure
    # a deterministic output order as required.
    for field in sorted(list(all_fields)):
        # Retrieve values, using the MISSING sentinel for keys not present.
        before_value = previous.get(field, MISSING)
        after_value = current.get(field, MISSING)

        if before_value != after_value:
            # SRL-3: Every field-level change must be represented as an explicit
            # record with field, before, and after.
            # SRL-3: Do not collapse multiple changed fields into a summary string.
            record = {
                "field": field,
                "before": before_value,
                "after": after_value,
            }
            diff_records.append(record)

    return diff_records
