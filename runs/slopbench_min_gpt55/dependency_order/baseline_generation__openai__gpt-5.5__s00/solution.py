from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Return parallelizable execution batches for tasks with prerequisites.

    Each key in ``dependencies`` is a task, and its value lists tasks that must
    be completed before it. Tasks that appear only as prerequisites are included
    in the returned plan. If the dependency graph contains a cycle, ValueError
    is raised.
    """
    all_tasks: set[str] = set(dependencies)
    prerequisites_by_task: dict[str, set[str]] = {}

    for task, prerequisites in dependencies.items():
        prerequisite_set = set(prerequisites)
        prerequisites_by_task[task] = prerequisite_set
        all_tasks.update(prerequisite_set)

    dependents_by_task: dict[str, set[str]] = {task: set() for task in all_tasks}
    remaining_prerequisite_count: dict[str, int] = {}

    for task in all_tasks:
        remaining_prerequisite_count[task] = len(prerequisites_by_task.get(task, set()))

    for task, prerequisites in prerequisites_by_task.items():
        for prerequisite in prerequisites:
            dependents_by_task[prerequisite].add(task)

    ready = sorted(
        task for task in all_tasks if remaining_prerequisite_count[task] == 0
    )
    batches: list[list[str]] = []
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        next_ready: list[str] = []
        for completed_task in batch:
            for dependent in dependents_by_task[completed_task]:
                remaining_prerequisite_count[dependent] -= 1
                if remaining_prerequisite_count[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed_count != len(all_tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches
