"""
A module for tracking the difference between two dictionary states.
"""

def diff_versions(previous: dict, current: dict) -> list[dict]:
    """
    Compares two dictionary states and returns a list of changes.

    A change is recorded for any field that was added, removed, or had its
    value modified.

    Args:
        previous: A dictionary representing the previous state.
        current: A dictionary representing the current state.

    Returns:
        A list of dictionaries, where each dictionary represents a single
        field change. Each record contains the 'field' name, its value
        'before' the change, and its value 'after' the change. The list
        is sorted alphabetically by field name.
        - For added fields, 'before' is None.
        - For removed fields, 'after' is None.
    """
    all_keys = set(previous.keys()) | set(current.keys())
    diff_records = []

    for key in sorted(all_keys):
        in_previous = key in previous
        in_current = key in current

        previous_value = previous.get(key)
        current_value = current.get(key)

        if not in_previous:
            # Field was added
            diff_records.append({
                "field": key,
                "before": None,
                "after": current_value,
            })
        elif not in_current:
            # Field was removed
            diff_records.append({
                "field": key,
                "before": previous_value,
                "after": None,
            })
        elif previous_value != current_value:
            # Field value was changed
            diff_records.append({
                "field": key,
                "before": previous_value,
                "after": current_value,
            })

    return diff_records
