"""
dependency_order.py

Provides plan_batches: topological sort returning parallel execution batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map (task -> list of prerequisite tasks),
    return a list of batches where each batch is a sorted list of tasks
    that can run in parallel. Tasks in earlier batches must complete
    before tasks in later batches begin.

    Raises ValueError if a cycle is detected.
    """
    # Build a complete set of nodes (including those only appearing as deps)
    all_nodes: set[str] = set()
    for task, deps in dependencies.items():
        all_nodes.add(task)
        for dep in deps:
            all_nodes.add(dep)

    # Build in-degree map and adjacency list (dep -> dependents)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    # adj maps a node to the set of nodes that depend on it
    adj: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, deps in dependencies.items():
        for dep in deps:
            # dep must come before task
            adj[dep].append(task)
            in_degree[task] += 1

    # Kahn's algorithm
    queue: deque[str] = deque()
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)

    batches: list[list[str]] = []
    visited_count = 0

    while queue:
        # All nodes currently in queue form the current batch
        current_batch = sorted(queue)
        batches.append(current_batch)
        visited_count += len(current_batch)

        queue.clear()
        next_nodes: list[str] = []
        for node in current_batch:
            for dependent in adj[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_nodes.append(dependent)

        for node in next_nodes:
            queue.append(node)

    if visited_count != len(all_nodes):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
