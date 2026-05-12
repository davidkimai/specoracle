"""
dependency_order.py

Provides plan_batches(dependencies) which performs a topological sort and
returns batches of tasks that can run in parallel.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map (task -> list of prerequisite tasks), return a list
    of batches. Each batch is a sorted list of tasks that can run in parallel
    (all their prerequisites have been completed in earlier batches).

    Raises ValueError if the graph contains a cycle.
    """
    # Build a complete set of nodes (include tasks that only appear as deps)
    all_nodes: set[str] = set(dependencies.keys())
    for prereqs in dependencies.values():
        all_nodes.update(prereqs)

    # Build in-degree map and adjacency list (prerequisite -> dependents)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            dependents[prereq].append(task)
            in_degree[task] += 1

    # Kahn's algorithm with level tracking
    queue: deque[str] = deque()
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)

    batches: list[list[str]] = []
    processed: int = 0

    while queue:
        # All nodes currently in the queue form one batch
        batch_size = len(queue)
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
        raise ValueError("Cycle detected in the dependency graph")

    return batches
