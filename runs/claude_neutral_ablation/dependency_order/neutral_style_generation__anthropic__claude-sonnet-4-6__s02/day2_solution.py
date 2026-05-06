"""
dependency_order.py

Implements plan_batches: topological level-order scheduling with cycle detection.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Given a dependency map {task: [prerequisite_tasks]}, return a list of
    batches (each batch is a sorted list of tasks) that can be executed in
    parallel, respecting dependency ordering.

    If completed is provided, those tasks are treated as already done and are
    omitted from the returned batches, but they still satisfy dependencies for
    remaining tasks.

    Raises ValueError if the dependency graph contains a cycle.
    """
    done: set[str] = set(completed) if completed else set()

    # Build a complete set of nodes (including tasks that only appear as deps)
    all_nodes: set[str] = set()
    for task, prereqs in dependencies.items():
        all_nodes.add(task)
        for p in prereqs:
            all_nodes.add(p)

    # in_degree[node] = number of prerequisites still outstanding
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}

    # dependents[node] = list of tasks that depend on node
    dependents: dict[str, list[str]] = {node: [] for node in all_nodes}

    for task, prereqs in dependencies.items():
        # Deduplicate prereqs to avoid double-counting in_degree
        seen: set[str] = set()
        for p in prereqs:
            if p not in seen:
                seen.add(p)
                # If this prereq is already completed, don't count it
                if p not in done:
                    in_degree[task] += 1
                    dependents[p].append(task)

    # Seed the queue: nodes with no outstanding prerequisites.
    # Completed nodes start as "processed" without appearing in batches.
    queue: deque[str] = deque()
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)

    batches: list[list[str]] = []
    processed = 0

    while queue:
        # Collect all nodes currently available (current level)
        current_batch = sorted(queue)
        queue.clear()

        # Separate into tasks to emit vs already-completed tasks
        emit_batch = [node for node in current_batch if node not in done]
        if emit_batch:
            batches.append(emit_batch)

        for node in current_batch:
            processed += 1
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    if processed != len(all_nodes):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
