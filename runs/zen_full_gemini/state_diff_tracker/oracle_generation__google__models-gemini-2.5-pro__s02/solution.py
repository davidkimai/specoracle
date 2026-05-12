"""
A module for tracking state differences between dictionary-based versions.
"""

from typing import Any, Dict, List, Set, Union

# A ChangeRecord represents a single atomic change to a field.
ChangeRecord = Dict[str, Union[str, Any]]


def diff_versions(
    previous: Dict[str, Any], current: Dict[str, Any]
) -> List[ChangeRecord]:
    """
    Compares two dictionary versions and returns a list of field-level changes.

    This function identifies fields that were added, removed, or had their
    values modified between the 'previous' and 'current' states.

    In accordance with SRL-3, every field-level change is represented as an
    explicit record containing the field name, the value before the change,
    and the value after the change.

    Args:
        previous: A dictionary representing the state before the change.
        current: A dictionary representing the state after the change.

    Returns:
        A list of dictionaries, where each dictionary represents a single
        field change. Each record contains 'field', 'before', and 'after'
        keys. The list is sorted alphabetically by the 'field' name.
        - 'field': The name of the key that changed.
        - 'before': The value of the field in the 'previous' dictionary.
                    This is None if the field was newly added.
        - 'after': The value of the field in the 'current' dictionary.
                   This is None if the field was removed.
    """
    changes: List[ChangeRecord] = []
    all_fields: Set[str] = previous.keys() | current.keys()

    for field in sorted(list(all_fields)):
        before_value = previous.get(field)
        after_value = current.get(field)

        if before_value != after_value:
            change_record: ChangeRecord = {
                "field": field,
                "before": before_value,
                "after": after_value,
            }
            changes.append(change_record)

    return changes
