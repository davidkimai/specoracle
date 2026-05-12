"""
dependency_order.py

Provides plan_batches: topological sort returning parallel batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map {task: [prerequisites]}, return a list of batches
    where each batch contains tasks that can run in parallel (all prerequisites
    satisfied by prior batches). Each batch is sorted alphabetically.

    Raises ValueError if the dependency graph contains a cycle.
    """
    # Build a complete set of nodes (include tasks only appearing as deps)
    all_nodes: set[str] = set(dependencies.keys())
    for prereqs in dependencies.values():
        all_nodes.update(prereqs)

    # Build in-degree map and adjacency list (prereq -> dependents)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            dependents[prereq].append(task)
            in_degree[task] += 1

    # Kahn's algorithm
    queue: deque[str] = deque(
        node for node in all_nodes if in_degree[node] == 0
    )

    batches: list[list[str]] = []
    processed: int = 0

    while queue:
        # Take all nodes currently in the queue as a batch
        batch = sorted(queue)
        batches.append(batch)
        queue.clear()

        for task in batch:
            processed += 1
            for dependent in dependents[task]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    if processed != len(all_nodes):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
