def diff_versions(previous: dict, current: dict) -> list[dict]:
    all_fields = set(previous.keys()) | set(current.keys())
    records = []
    for field in all_fields:
        before = previous.get(field)
        after = current.get(field)
        if before != after:
            records.append({
                "field": field,
                "before": before,
                "after": after,
            })
    records.sort(key=lambda r: r["field"])
    return records
