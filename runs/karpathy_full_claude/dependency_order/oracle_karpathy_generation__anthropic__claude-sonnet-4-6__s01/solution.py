from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    # Build complete set of nodes (include tasks that only appear as dependencies)
    all_nodes = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    # Build in-degree and adjacency list
    in_degree = {node: 0 for node in all_nodes}
    # edge: dep -> node (dep must come before node)
    adj = {node: [] for node in all_nodes}

    for node, deps in dependencies.items():
        for dep in deps:
            adj[dep].append(node)
            in_degree[node] += 1

    # Kahn's algorithm
    queue = deque(sorted(node for node in all_nodes if in_degree[node] == 0))
    batches = []
    processed = 0

    while queue:
        batch = sorted(queue)
        queue.clear()
        batches.append(batch)
        processed += len(batch)
        next_batch = set()
        for node in batch:
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_batch.add(neighbor)
        for node in sorted(next_batch):
            queue.append(node)

    if processed != len(all_nodes):
        raise ValueError("Cycle detected in dependency graph")

    return batches
