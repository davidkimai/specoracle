from typing import Any


def diff_versions(previous: dict, current: dict) -> list[dict]:
    """
    Return a shallow field-level diff between two dictionaries.

    Each changed, added, or removed field is represented as:
        {"field": key, "before": old_value_or_None, "after": new_value_or_None}

    Records are sorted by field.
    """
    records: list[dict[str, Any]] = []

    all_fields = set(previous) | set(current)

    for field in sorted(all_fields):
        in_previous = field in previous
        in_current = field in current

        if not in_previous:
            records.append(
                {
                    "field": field,
                    "before": None,
                    "after": current[field],
                }
            )
        elif not in_current:
            records.append(
                {
                    "field": field,
                    "before": previous[field],
                    "after": None,
                }
            )
        elif previous[field] != current[field]:
            records.append(
                {
                    "field": field,
                    "before": previous[field],
                    "after": current[field],
                }
            )

    return records
