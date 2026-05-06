"""
dependency_order.py

Implements plan_batches: topological sort with parallel batching.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map (task -> list of tasks that must run before it),
    return batches of tasks that can run in parallel. Each batch is sorted
    alphabetically. Raises ValueError if a cycle is detected.

    Tasks that appear only as dependencies (not as keys) are included.
    The input is not mutated.
    """
    # Build a complete set of all nodes
    all_nodes: set[str] = set()
    for task, deps in dependencies.items():
        all_nodes.add(task)
        for dep in deps:
            all_nodes.add(dep)

    # Build adjacency and in-degree structures
    # in_degree[node] = number of prerequisites not yet satisfied
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    # dependents[node] = list of nodes that depend on node
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, deps in dependencies.items():
        for dep in deps:
            in_degree[task] += 1
            dependents[dep].append(task)

    # Kahn's algorithm
    queue: deque[str] = deque()
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)

    batches: list[list[str]] = []
    processed: int = 0

    while queue:
        # Current batch: all nodes with in_degree == 0
        batch = sorted(queue)
        batches.append(batch)
        queue.clear()

        for node in batch:
            processed += 1
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    if processed != len(all_nodes):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
