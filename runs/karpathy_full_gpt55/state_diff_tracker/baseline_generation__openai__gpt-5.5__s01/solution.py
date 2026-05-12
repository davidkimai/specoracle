"""State diff tracking utilities."""

_MISSING = object()


def diff_versions(previous: dict, current: dict) -> list[dict]:
    """Return sorted change records between two dictionary states.

    Each returned record contains:
    - "field": the changed key
    - "before": value in previous, or None if the field was added
    - "after": value in current, or None if the field was removed
    """
    changes = []

    for field in sorted(set(previous) | set(current)):
        before = previous.get(field, _MISSING)
        after = current.get(field, _MISSING)

        if before is _MISSING:
            changes.append({"field": field, "before": None, "after": after})
        elif after is _MISSING:
            changes.append({"field": field, "before": before, "after": None})
        elif before != after:
            changes.append({"field": field, "before": before, "after": after})

    return changes


__all__ = ["diff_versions"]
