"""
dependency_order.py

Implements plan_batches(dependencies) which performs a topological sort and
returns batches of tasks that can execute in parallel.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Given a dependency mapping (task -> list of prerequisite tasks),
    return a list of batches. Each batch contains tasks that can run
    in parallel (all their prerequisites have been completed in earlier
    batches). Tasks within each batch are sorted alphabetically.

    Raises ValueError if the dependency graph contains a cycle.
    """
    # Build a complete set of all tasks (including those only appearing as deps)
    all_tasks: set[str] = set()
    for task, prereqs in dependencies.items():
        all_tasks.add(task)
        for prereq in prereqs:
            all_tasks.add(prereq)

    # Build in-degree count and adjacency list
    # in_degree[task] = number of prerequisites not yet satisfied
    in_degree: dict[str, int] = {task: 0 for task in all_tasks}
    # successors[task] = list of tasks that depend on task
    successors: dict[str, list[str]] = {task: [] for task in all_tasks}

    for task, prereqs in dependencies.items():
        # Use deduplicated prereqs to avoid counting duplicates
        seen_prereqs: set[str] = set()
        for prereq in prereqs:
            if prereq not in seen_prereqs:
                seen_prereqs.add(prereq)
                in_degree[task] += 1
                successors[prereq].append(task)

    batches: list[list[str]] = []
    # Start with tasks that have no prerequisites
    ready = deque(sorted(task for task, deg in in_degree.items() if deg == 0))

    processed = 0

    while ready:
        # Current batch: all tasks currently ready
        current_batch = sorted(ready)
        batches.append(current_batch)
        ready.clear()

        next_ready: list[str] = []
        for task in current_batch:
            processed += 1
            for successor in successors[task]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    next_ready.append(successor)

        ready.extend(sorted(next_ready))

    if processed != len(all_tasks):
        raise ValueError(
            "Cycle detected in the dependency graph; topological sort is not possible."
        )

    return batches
