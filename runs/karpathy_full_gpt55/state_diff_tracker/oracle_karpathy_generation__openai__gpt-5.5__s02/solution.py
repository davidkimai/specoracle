_MISSING = object()


def diff_versions(previous: dict, current: dict) -> list[dict]:
    records = []

    for field in sorted(previous.keys() | current.keys()):
        before = previous.get(field, _MISSING)
        after = current.get(field, _MISSING)

        if before != after:
            records.append(
                {
                    "field": field,
                    "before": None if before is _MISSING else before,
                    "after": None if after is _MISSING else after,
                }
            )

    return records
