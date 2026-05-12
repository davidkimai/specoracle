"""State difference tracking utilities."""

from typing import Any


_MISSING = object()


def diff_versions(previous: dict, current: dict) -> list[dict]:
    """Return explicit field-level changes between two state dictionaries.

    Each returned record contains:
    - field: the changed field name/key
    - before: value in ``previous`` or None if the field was absent
    - after: value in ``current`` or None if the field is absent

    Records are sorted by field.
    """
    changes: list[dict[str, Any]] = []

    for field in sorted(set(previous) | set(current)):
        before = previous.get(field, _MISSING)
        after = current.get(field, _MISSING)

        if before is _MISSING and after is _MISSING:
            continue

        if before is _MISSING or after is _MISSING or before != after:
            changes.append(
                {
                    "field": field,
                    "before": None if before is _MISSING else before,
                    "after": None if after is _MISSING else after,
                }
            )

    return changes


__all__ = ["diff_versions"]
