"""State diff tracker module."""

from typing import Any


_MISSING = object()


def diff_versions(previous: dict, current: dict) -> list[dict]:
    """Return one explicit change record per changed field, sorted by field.

    Added fields are represented with ``before`` set to ``None``.
    Removed fields are represented with ``after`` set to ``None``.
    """
    changes: list[dict[str, Any]] = []

    for field in sorted(set(previous) | set(current)):
        before = previous.get(field, _MISSING)
        after = current.get(field, _MISSING)

        if before is _MISSING and after is _MISSING:
            continue

        if before is _MISSING:
            changes.append({"field": field, "before": None, "after": after})
        elif after is _MISSING:
            changes.append({"field": field, "before": before, "after": None})
        elif before != after:
            changes.append({"field": field, "before": before, "after": after})

    return changes
