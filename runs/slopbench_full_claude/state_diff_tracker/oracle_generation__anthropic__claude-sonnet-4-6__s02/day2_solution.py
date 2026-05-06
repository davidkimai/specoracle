def diff_versions(previous: dict, current: dict, as_graph: bool = False) -> list[dict] | dict:
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

    if not as_graph:
        return records

    nodes = {"previous", "current"}
    edges = [
        {"from": "previous", "to": "current", "label": r["field"]}
        for r in records
    ]
    return {"nodes": nodes, "edges": edges}
