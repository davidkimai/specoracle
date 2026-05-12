def diff_versions(previous: dict, current: dict) -> list[dict]:
    all_keys = set(previous.keys()) | set(current.keys())
    records = []
    for key in all_keys:
        before = previous.get(key)
        after = current.get(key)
        if key not in previous:
            records.append({"field": key, "before": None, "after": after})
        elif key not in current:
            records.append({"field": key, "before": before, "after": None})
        elif before != after:
            records.append({"field": key, "before": before, "after": after})
    records.sort(key=lambda r: r["field"])
    return records
