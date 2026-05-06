"""
dependency_order.py

Implements plan_batches(dependencies) which performs a topological sort and
returns batches of tasks that can execute in parallel.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Given a dependency mapping (task -> list of prerequisite tasks),
    return a list of batches. Each batch contains tasks that can run
    in parallel (all their prerequisites have been completed in earlier
    batches). Tasks within each batch are sorted alphabetically.

    If `completed` is provided, those tasks are treated as already done:
    they satisfy dependencies for remaining tasks but do not appear in
    any returned batch.

    Raises ValueError if the dependency graph contains a cycle.
    """
    completed = set(completed) if completed else set()

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

    # Tasks that are already completed satisfy their successors immediately.
    # Reduce in-degrees for successors of completed tasks and exclude
    # completed tasks from the remaining work.
    for task in completed:
        if task in successors:
            for successor in successors[task]:
                in_degree[successor] -= 1

    # The set of tasks we still need to schedule (excludes completed ones)
    remaining_tasks: set[str] = all_tasks - completed

    batches: list[list[str]] = []
    # Start with tasks that have no prerequisites (among remaining tasks)
    ready = deque(
        sorted(task for task in remaining_tasks if in_degree[task] == 0)
    )

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
                if in_degree[successor] == 0 and successor not in completed:
                    next_ready.append(successor)

        ready.extend(sorted(next_ready))

    if processed != len(remaining_tasks):
        raise ValueError(
            "Cycle detected in the dependency graph; topological sort is not possible."
        )

    return batches
