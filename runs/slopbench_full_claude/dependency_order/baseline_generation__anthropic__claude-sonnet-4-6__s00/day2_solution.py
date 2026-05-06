"""
dependency_order.py

Implements plan_batches: topological sort with parallel batching.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Given a dependency map (task -> list of tasks that must run before it),
    return batches of tasks that can run in parallel. Each batch is sorted
    alphabetically. Raises ValueError if a cycle is detected.

    Tasks that appear only as dependencies (not as keys) are included.
    The input is not mutated.

    If `completed` is provided, those tasks are treated as already done:
    they are omitted from the returned batches but still satisfy dependencies
    for remaining tasks.
    """
    done: set[str] = set(completed) if completed else set()

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

    # Nodes that are already completed satisfy their dependents immediately.
    # Reduce in-degrees accordingly and exclude completed nodes from processing.
    for node in done:
        if node in in_degree:
            for dependent in dependents.get(node, []):
                in_degree[dependent] -= 1

    # The set of nodes we actually need to schedule (excluding completed ones)
    remaining_nodes: set[str] = all_nodes - done

    # Kahn's algorithm over remaining nodes only
    queue: deque[str] = deque()
    for node in remaining_nodes:
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
                if dependent in remaining_nodes:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

    if processed != len(remaining_nodes):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
