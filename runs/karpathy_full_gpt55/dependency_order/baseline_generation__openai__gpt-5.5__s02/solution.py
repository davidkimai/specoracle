from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Plan tasks into parallelizable batches based on prerequisite dependencies.

    Args:
        dependencies: Mapping from a task name to the list of tasks that must be
            completed before it.

    Returns:
        A list of batches. Each batch contains tasks that can be run in parallel,
        sorted alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle.
    """
    all_tasks: set[str] = set(dependencies)
    for prerequisites in dependencies.values():
        all_tasks.update(prerequisites)

    dependents: dict[str, set[str]] = {task: set() for task in all_tasks}
    remaining_prerequisites: dict[str, int] = {task: 0 for task in all_tasks}

    for task, prerequisites in dependencies.items():
        unique_prerequisites = set(prerequisites)
        remaining_prerequisites[task] = len(unique_prerequisites)
        for prerequisite in unique_prerequisites:
            dependents[prerequisite].add(task)

    batches: list[list[str]] = []
    ready = sorted(
        task for task, count in remaining_prerequisites.items() if count == 0
    )
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        newly_ready: list[str] = []
        for completed_task in batch:
            for dependent in dependents[completed_task]:
                remaining_prerequisites[dependent] -= 1
                if remaining_prerequisites[dependent] == 0:
                    newly_ready.append(dependent)

        ready = sorted(newly_ready)

    if completed_count != len(all_tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches
