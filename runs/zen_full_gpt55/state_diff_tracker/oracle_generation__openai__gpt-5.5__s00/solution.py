def diff_versions(previous: dict, current: dict) -> list[dict]:
    missing = object()
    records = []

    for field in sorted(set(previous) | set(current)):
        before = previous.get(field, missing)
        after = current.get(field, missing)

        if before is missing or after is missing or before != after:
            records.append(
                {
                    "field": field,
                    "before": None if before is missing else before,
                    "after": None if after is missing else after,
                }
            )

    return records
