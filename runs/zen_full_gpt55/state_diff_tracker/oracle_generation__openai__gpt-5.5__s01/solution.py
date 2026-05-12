from typing import Any


_MISSING = object()


def diff_versions(previous: dict, current: dict) -> list[dict]:
    """
    Return one explicit change record for each top-level field that was added,
    removed, or whose value changed.

    Missing values are represented as None in the returned record.
    """
    records: list[dict[str, Any]] = []

    for field in sorted(set(previous) | set(current)):
        before = previous.get(field, _MISSING)
        after = current.get(field, _MISSING)

        if before is _MISSING or after is _MISSING or before != after:
            records.append(
                {
                    "field": field,
                    "before": None if before is _MISSING else before,
                    "after": None if after is _MISSING else after,
                }
            )

    return records
