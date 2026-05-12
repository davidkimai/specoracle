from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    # Build complete node set including implicit dependency-only nodes
    all_nodes = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    # Build in-degree and adjacency list
    in_degree = {node: 0 for node in all_nodes}
    dependents = {node: [] for node in all_nodes}  # node -> list of nodes that depend on it

    for node, deps in dependencies.items():
        for dep in deps:
            dependents[dep].append(node)
            in_degree[node] += 1

    # Kahn's algorithm
    queue = deque(sorted(n for n in all_nodes if in_degree[n] == 0))
    batches = []
    processed = 0

    while queue:
        batch = sorted(queue)
        queue.clear()
        batches.append(batch)
        processed += len(batch)
        next_batch = set()
        for node in batch:
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_batch.add(dependent)
        queue.extend(sorted(next_batch))

    if processed != len(all_nodes):
        raise ValueError("Cycle detected in dependency graph")

    return batches
