from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Return alphabetical parallel execution batches for the dependency graph.

    Each key is a task and each value lists tasks that must complete before it.
    Tasks that appear only as dependencies are included. The input is not mutated.

    Raises:
        ValueError: if the dependency graph contains a cycle.
    """
    tasks: set[str] = set(dependencies)
    for prereqs in dependencies.values():
        tasks.update(prereqs)

    remaining = {task: 0 for task in tasks}
    dependents = {task: [] for task in tasks}

    for task, prereqs in dependencies.items():
        remaining[task] = len(prereqs)
        for prereq in prereqs:
            dependents[prereq].append(task)

    ready = sorted(task for task in tasks if remaining[task] == 0)
    batches: list[list[str]] = []
    completed = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed += len(batch)

        next_ready: list[str] = []
        for task in batch:
            for dependent in dependents[task]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed != len(tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches
