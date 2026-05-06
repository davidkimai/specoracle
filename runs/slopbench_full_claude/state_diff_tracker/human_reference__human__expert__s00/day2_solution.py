from __future__ import annotations


def diff_versions(
    previous: dict,
    current: dict,
    as_graph: bool = False,
) -> list[dict] | dict:
    changes = []
    for field in sorted(set(previous) | set(current)):
        before = previous.get(field)
        after = current.get(field)
        if before != after:
            changes.append({'field': field, 'before': before, 'after': after})

    if not as_graph:
        return changes

    nodes = [
        {'id': 'previous', 'data': previous},
        {'id': 'current', 'data': current},
    ]
    edges = [
        {'source': 'previous', 'target': 'current', 'label': change['field'],
         'before': change['before'], 'after': change['after']}
        for change in changes
    ]
    return {'nodes': nodes, 'edges': edges}
