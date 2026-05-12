from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    # Build complete node set and in-degree map
    in_degree = {}
    graph = {}  # node -> list of nodes that depend on it

    # Collect all nodes
    all_nodes = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    for node in all_nodes:
        in_degree[node] = 0
        graph[node] = []

    for task, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(task)
            in_degree[task] += 1

    # Kahn's algorithm
    batches = []
    queue = deque(node for node in all_nodes if in_degree[node] == 0)

    while queue:
        batch = sorted(queue)
        batches.append(batch)
        queue.clear()
        for node in batch:
            for dependent in graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    if sum(len(b) for b in batches) != len(all_nodes):
        raise ValueError("Cycle detected in dependency graph")

    return batches
