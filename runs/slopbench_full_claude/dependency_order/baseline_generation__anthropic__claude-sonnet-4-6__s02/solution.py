"""
dependency_order.py

Implements plan_batches for topological ordering of tasks into parallel batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency map, return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose dependencies have all been
    completed in previous batches. Raises ValueError if a cycle is detected.

    :param dependencies: Maps task -> list of tasks that must complete first.
    :return: List of batches (each batch is a sorted list of task names).
    """
    # Build a complete set of all tasks (including those only appearing as deps)
    all_tasks: set[str] = set(dependencies.keys())
    for deps in dependencies.values():
        all_tasks.update(deps)

    # Build adjacency and in-degree structures
    # in_degree[task] = number of tasks that must complete before task
    in_degree: dict[str, int] = {task: 0 for task in all_tasks}
    # successors[task] = list of tasks that depend on task
    successors: dict[str, list[str]] = {task: [] for task in all_tasks}

    for task, deps in dependencies.items():
        for dep in deps:
            successors[dep].append(task)
            in_degree[task] += 1

    # Kahn's algorithm for topological sort in batches
    queue: deque[str] = deque()
    for task in all_tasks:
        if in_degree[task] == 0:
            queue.append(task)

    batches: list[list[str]] = []
    processed_count = 0

    while queue:
        # Sort current batch alphabetically
        current_batch = sorted(queue)
        batches.append(current_batch)
        queue.clear()

        for task in current_batch:
            processed_count += 1
            for successor in successors[task]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)

    if processed_count != len(all_tasks):
        raise ValueError("Cycle detected in dependency graph.")

    return batches
