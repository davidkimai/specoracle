"""
dependency_order.py

Provides plan_batches: topological sort returning parallel execution batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map (task -> list of prerequisite tasks), return
    an ordered list of batches. Each batch is a list of tasks (sorted
    alphabetically) that can run in parallel once all previous batches
    complete.

    Raises ValueError if the graph contains a cycle.
    """
    # Build a complete set of nodes (including implicit ones from dep lists)
    all_nodes: set[str] = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    # Build in-degree map and adjacency list (prerequisite -> dependents)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            dependents[prereq].append(task)
            in_degree[task] += 1

    # Kahn's algorithm with batching
    queue: deque[str] = deque(
        sorted(node for node, deg in in_degree.items() if deg == 0)
    )
    batches: list[list[str]] = []
    processed: int = 0

    while queue:
        # All nodes currently in the queue form the current batch
        batch_size = len(queue)
        batch = []
        for _ in range(batch_size):
            node = queue.popleft()
            batch.append(node)
            processed += 1
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        batch.sort()
        batches.append(batch)
        # Re-sort queue for deterministic ordering within next batch
        # (nodes may have been added in arbitrary order)
        sorted_queue = sorted(queue)
        queue.clear()
        queue.extend(sorted_queue)

    if processed != len(all_nodes):
        raise ValueError("Cycle detected in dependency graph")

    return batches
