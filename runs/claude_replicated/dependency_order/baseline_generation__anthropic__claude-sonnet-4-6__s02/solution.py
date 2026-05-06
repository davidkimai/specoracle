"""
dependency_order.py

Implements plan_batches for topological batch scheduling.
"""

from collections import defaultdict, deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map {task: [prerequisite_tasks]}, return batches of
    tasks that can run in parallel. Each batch is sorted alphabetically.
    Raises ValueError if the graph contains a cycle.
    """
    # Build the complete set of nodes (including tasks only mentioned as deps)
    all_nodes: set[str] = set()
    for task, deps in dependencies.items():
        all_nodes.add(task)
        for dep in deps:
            all_nodes.add(dep)

    # Build in-degree count and adjacency list (dep -> dependents)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    dependents: dict[str, list[str]] = defaultdict(list)

    for task, deps in dependencies.items():
        # Use a set to avoid counting duplicate deps multiple times
        unique_deps = set(deps)
        for dep in unique_deps:
            dependents[dep].append(task)
            in_degree[task] += 1

    # Kahn's algorithm for topological sort in batches
    batches: list[list[str]] = []
    queue: deque[str] = deque(sorted(node for node, deg in in_degree.items() if deg == 0))
    visited_count = 0

    while queue:
        # Process all nodes with in_degree == 0 as a batch
        batch_size = len(queue)
        current_batch = sorted(queue)
        batches.append(current_batch)
        visited_count += batch_size

        # Drain queue and process next level
        queue.clear()
        next_level: list[str] = []
        for node in current_batch:
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_level.append(dependent)
        # Sort next level before adding to queue for determinism
        for node in sorted(next_level):
            queue.append(node)

    if visited_count != len(all_nodes):
        raise ValueError("Cycle detected in dependency graph")

    return batches
