_MISSING = object()


def diff_versions(previous: dict, current: dict) -> list[dict]:
    """
    Return one change record for each field whose value differs between versions.

    Added fields have before set to None. Removed fields have after set to None.
    Records are sorted by field.
    """
    if not isinstance(previous, dict):
        raise TypeError("previous must be a dict")
    if not isinstance(current, dict):
        raise TypeError("current must be a dict")

    changes: list[dict] = []

    for field in sorted(set(previous) | set(current)):
        before = previous.get(field, _MISSING)
        after = current.get(field, _MISSING)

        if before is _MISSING or after is _MISSING or before != after:
            changes.append(
                {
                    "field": field,
                    "before": None if before is _MISSING else before,
                    "after": None if after is _MISSING else after,
                }
            )

    return changes
