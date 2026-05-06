"""
dependency_order.py

Provides plan_batches: topological-sort a dependency graph into parallel batches.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Given a mapping of task -> [prerequisite tasks], return a list of batches
    where each batch is a sorted list of tasks that can run in parallel.

    Tasks that only appear as dependencies (not as keys) are included.
    Raises ValueError if the graph contains a cycle.
    Does not mutate the input.

    Optional keyword argument:
        completed: set of tasks already done. These are excluded from the
                   returned batches but still satisfy dependencies for
                   remaining tasks.
    """
    done: set[str] = set(completed) if completed else set()

    # Build a complete set of all nodes (including implicit dependency-only nodes)
    all_nodes: set[str] = set(dependencies.keys())
    for deps in dependencies.values():
        all_nodes.update(deps)

    # Build in-degree map and adjacency list (dep -> dependents)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            # prereq must finish before task
            dependents[prereq].append(task)
            in_degree[task] += 1

    # Treat completed tasks as already processed: reduce in-degrees of their
    # dependents, then remove them from the node set we need to schedule.
    for node in done:
        if node in all_nodes:
            for dependent in dependents.get(node, []):
                in_degree[dependent] -= 1

    # Only schedule nodes that are not already completed
    remaining_nodes = all_nodes - done

    # Kahn's algorithm over remaining nodes
    batches: list[list[str]] = []
    queue: deque[str] = deque(
        sorted(node for node in remaining_nodes if in_degree[node] == 0)
    )

    processed = 0

    while queue:
        # All nodes currently in the queue have in-degree 0 → one batch
        batch_size = len(queue)
        batch = []
        for _ in range(batch_size):
            node = queue.popleft()
            batch.append(node)
            processed += 1
            for dependent in dependents[node]:
                if dependent in done:
                    continue
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Sort the batch alphabetically
        batch.sort()
        batches.append(batch)

        # Re-sort the queue for deterministic ordering within the next batch
        sorted_queue = sorted(queue)
        queue.clear()
        queue.extend(sorted_queue)

    if processed != len(remaining_nodes):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
