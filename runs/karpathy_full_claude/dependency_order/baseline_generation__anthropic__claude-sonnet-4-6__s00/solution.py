"""
dependency_order module
Provides plan_batches for topological ordering with parallel batching.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map (task -> list of tasks that must run before it),
    return a list of batches. Each batch is a list of tasks that can run in
    parallel (all their dependencies have been satisfied by previous batches).
    Tasks within each batch are sorted alphabetically.

    Raises ValueError if the graph contains a cycle.
    """
    # Build a complete set of all nodes (including those only appearing as deps)
    all_nodes: set[str] = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    # Build in-degree map and adjacency list (dep -> list of tasks that depend on dep)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, deps in dependencies.items():
        for dep in deps:
            in_degree[task] += 1
            dependents[dep].append(task)

    # Kahn's algorithm with batching
    # Start with all nodes that have no dependencies
    queue: deque[str] = deque(
        sorted(node for node in all_nodes if in_degree[node] == 0)
    )

    batches: list[list[str]] = []
    processed_count = 0

    while queue:
        # Current level: all nodes currently in queue
        batch_size = len(queue)
        current_batch = sorted(queue)
        batches.append(current_batch)
        queue.clear()

        next_level: list[str] = []
        for node in current_batch:
            processed_count += 1
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_level.append(dependent)

        # Add next level nodes to queue, sorted for determinism
        for node in sorted(next_level):
            queue.append(node)

    if processed_count != len(all_nodes):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
