"""
dependency_order.py

Implements plan_batches for topological ordering of tasks into parallel batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map where dependencies[task] = [list of tasks that must
    complete before task], return a list of batches. Each batch is a list of
    tasks that can run in parallel (sorted alphabetically). Tasks in earlier
    batches have no dependencies on tasks in later batches.

    Raises ValueError if the graph contains a cycle.
    Includes tasks that only appear as dependencies (not as keys).
    Does not mutate the input.
    """
    # Build a complete set of all nodes (including those only in dep lists)
    all_nodes: set[str] = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    # Build in-degree map and adjacency list (edge: dep -> task)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    # adjacency: for each node, which nodes depend on it
    adjacency: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, deps in dependencies.items():
        for dep in deps:
            adjacency[dep].append(task)
            in_degree[task] += 1

    # Kahn's algorithm for topological sort in batches
    batches: list[list[str]] = []
    queue: deque[str] = deque()

    # Start with nodes that have no dependencies
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)

    processed_count = 0

    while queue:
        # Current batch: all nodes currently in the queue
        batch_size = len(queue)
        current_batch = sorted(queue)
        batches.append(current_batch)

        # Drain the queue for this batch
        queue.clear()

        for node in current_batch:
            processed_count += 1
            for dependent in adjacency[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    if processed_count != len(all_nodes):
        raise ValueError("Graph contains a cycle")

    return batches
