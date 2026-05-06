from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Plan tasks into parallelizable batches based on prerequisite dependencies.

    Args:
        dependencies: A mapping from task name to the list of task names that
            must be completed before it.

    Returns:
        A list of batches. Each batch contains task names that can be run in
        parallel, sorted alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle.
    """
    prerequisite_map: dict[str, set[str]] = {
        task: set(prerequisites)
        for task, prerequisites in dependencies.items()
    }

    all_tasks: set[str] = set(prerequisite_map)
    for prerequisites in prerequisite_map.values():
        all_tasks.update(prerequisites)

    for task in all_tasks:
        prerequisite_map.setdefault(task, set())

    dependents: dict[str, set[str]] = {task: set() for task in all_tasks}
    remaining_prerequisites: dict[str, int] = {}

    for task, prerequisites in prerequisite_map.items():
        remaining_prerequisites[task] = len(prerequisites)
        for prerequisite in prerequisites:
            dependents[prerequisite].add(task)

    ready = sorted(
        task for task in all_tasks
        if remaining_prerequisites[task] == 0
    )

    batches: list[list[str]] = []
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


__all__ = ["plan_batches"]
