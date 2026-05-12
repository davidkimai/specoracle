def diff_versions(previous: dict, current: dict) -> list[dict]:
    all_fields = set(previous.keys()) | set(current.keys())
    records = []
    for field in sorted(all_fields):
        before = previous.get(field)
        after = current.get(field)
        if before != after:
            records.append({"field": field, "before": before, "after": after})
    return records
