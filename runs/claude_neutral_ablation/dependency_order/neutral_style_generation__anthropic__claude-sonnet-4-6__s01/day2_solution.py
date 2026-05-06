"""
dependency_order.py

Provides plan_batches: topological sort returning parallel execution batches.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Given a dependency map (task -> list of prerequisite tasks), return
    an ordered list of batches. Each batch is a list of tasks (sorted
    alphabetically) that can run in parallel once all previous batches
    complete.

    If completed is provided, those tasks are treated as already done:
    they satisfy dependencies for remaining tasks but do not appear in
    the returned batches.

    Raises ValueError if the graph contains a cycle.
    """
    done: set[str] = set(completed) if completed is not None else set()

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

    # Treat completed tasks as already processed: reduce in-degrees of their
    # dependents and remove them from the node set to be scheduled.
    for node in done:
        if node in all_nodes:
            for dependent in dependents.get(node, []):
                in_degree[dependent] -= 1

    # Nodes that still need scheduling
    remaining: set[str] = all_nodes - done

    # Kahn's algorithm with batching (only over remaining nodes)
    queue: deque[str] = deque(
        sorted(node for node in remaining if in_degree[node] == 0)
    )
    batches: list[list[str]] = []
    processed: int = 0

    while queue:
        batch_size = len(queue)
        batch = []
        for _ in range(batch_size):
            node = queue.popleft()
            batch.append(node)
            processed += 1
            for dependent in dependents[node]:
                if dependent in remaining:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        batch.sort()
        batches.append(batch)
        sorted_queue = sorted(queue)
        queue.clear()
        queue.extend(sorted_queue)

    if processed != len(remaining):
        raise ValueError("Cycle detected in dependency graph")

    return batches
