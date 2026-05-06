def diff_versions(previous: dict, current: dict, as_graph: bool = False) -> list[dict] | dict:
    all_fields = set(previous.keys()) | set(current.keys())
    records = []
    for field in all_fields:
        before = previous.get(field)
        after = current.get(field)
        if field not in previous:
            records.append({"field": field, "before": None, "after": after})
        elif field not in current:
            records.append({"field": field, "before": before, "after": None})
        elif before != after:
            records.append({"field": field, "before": before, "after": after})
    records.sort(key=lambda r: r["field"])

    if not as_graph:
        return records

    nodes = [
        {"id": "previous", "data": previous},
        {"id": "current", "data": current},
    ]
    edges = [
        {"from": "previous", "to": "current", "label": r["field"]}
        for r in records
    ]
    return {"nodes": nodes, "edges": edges}
