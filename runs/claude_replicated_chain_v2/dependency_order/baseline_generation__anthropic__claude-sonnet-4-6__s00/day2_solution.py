"""
dependency_order.py

Provides plan_batches: topological sort returning parallel batches.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Given a dependency map {task: [prerequisites]}, return a list of batches
    where each batch contains tasks that can run in parallel (all prerequisites
    satisfied by prior batches). Each batch is sorted alphabetically.

    If `completed` is provided, those tasks are treated as already finished:
    they satisfy dependencies for remaining tasks but do not appear in any
    returned batch.

    Raises ValueError if the dependency graph contains a cycle.
    """
    done: set[str] = set(completed) if completed else set()

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

    # Pre-satisfy dependencies from completed tasks:
    # reduce in_degree for dependents of completed nodes.
    # We do this by treating completed nodes as already processed.
    for node in done:
        if node in all_nodes:
            for dependent in dependents[node]:
                in_degree[dependent] -= 1

    # Kahn's algorithm — seed with nodes that have in_degree 0 and are not done
    queue: deque[str] = deque(
        node for node in all_nodes if in_degree[node] == 0 and node not in done
    )

    batches: list[list[str]] = []
    # Count nodes we need to process (excluding already-completed ones)
    remaining_nodes = all_nodes - done
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
                if in_degree[dependent] == 0 and dependent not in done:
                    queue.append(dependent)

    if processed != len(remaining_nodes):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
